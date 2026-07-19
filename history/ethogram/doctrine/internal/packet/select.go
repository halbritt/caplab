package packet

import (
	"fmt"
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"
)

func matchingSignal(condition string, signals []string) (string, bool) {
	normalizedCondition := normalize(condition)
	for _, signal := range signals {
		normalizedSignal := normalize(signal)
		if normalizedCondition == normalizedSignal || strings.Contains(normalizedSignal, normalizedCondition) {
			return signal, true
		}
	}
	return "", false
}

func phraseInText(phrase, text string) bool {
	phrase = normalize(phrase)
	text = normalize(text)
	if phrase == "" {
		return false
	}
	searchFrom := 0
	for searchFrom <= len(text) {
		relative := strings.Index(text[searchFrom:], phrase)
		if relative < 0 {
			return false
		}
		start := searchFrom + relative
		end := start + len(phrase)
		beforeWord := false
		if start > 0 {
			runeValue, _ := utf8.DecodeLastRuneInString(text[:start])
			beforeWord = isWordRune(runeValue)
		}
		afterWord := false
		if end < len(text) {
			runeValue, _ := utf8.DecodeRuneInString(text[end:])
			afterWord = isWordRune(runeValue)
		}
		if !beforeWord && !afterWord {
			return true
		}
		searchFrom = start + 1
	}
	return false
}

func isWordRune(value rune) bool {
	return value == '_' || unicode.IsLetter(value) || unicode.IsNumber(value)
}

func languageGateFailure(route object, languages []string) string {
	routeLanguages := map[string]bool{}
	for _, language := range asStrings(route["activate_for_languages"]) {
		routeLanguages[normalize(language)] = true
	}
	if routeLanguages["language-independent"] {
		return ""
	}
	requested := append([]string(nil), languages...)
	for _, language := range languages {
		normalized := normalize(language)
		if routeLanguages[normalized] {
			return ""
		}
	}
	routes := make([]string, 0, len(routeLanguages))
	for language := range routeLanguages {
		routes = append(routes, language)
	}
	sort.Strings(routes)
	sort.Strings(requested)
	return fmt.Sprintf("route languages %s include neither 'language-independent' nor a requested language %s", pythonList(routes), pythonList(requested))
}

func pythonList(values []string) string {
	quoted := make([]string, 0, len(values))
	for _, value := range values {
		quoted = append(quoted, fmt.Sprintf("'%s'", value))
	}
	return "[" + strings.Join(quoted, ", ") + "]"
}

func exclusionFailure(route object, signals []string) string {
	for _, condition := range asStrings(route["exclude_when"]) {
		if normalize(condition) == "never" {
			continue
		}
		if signal, ok := matchingSignal(condition, signals); ok {
			return fmt.Sprintf("exclude_when condition '%s' matched signal '%s'", condition, signal)
		}
	}
	return ""
}

func additionalGateFailures(route object, request retrievalRequest, reasons []string) []string {
	var failures []string
	roles := asStrings(route["activate_for_role_families"])
	if len(roles) == 0 {
		roles = asStrings(route["activate_for_roles"])
	}
	if !contains(roles, request.role) {
		failures = append(failures, fmt.Sprintf("role '%s' not in activate_for_roles", request.role))
	}
	primaryFamily := contains(asStrings(route["activate_for_task_families"]), request.taskFamily)
	conditionalFamily := contains(asStrings(route["conditional_for_task_families"]), request.taskFamily)
	contextualTaskMatch := contains(asStrings(route["activate_for_tasks"]), request.taskFamily)
	for _, reason := range reasons {
		if strings.HasPrefix(reason, "question term") || strings.HasPrefix(reason, "task variant") {
			contextualTaskMatch = true
		}
	}
	if !primaryFamily && !(conditionalFamily && contextualTaskMatch) {
		failures = append(failures, fmt.Sprintf("task '%s' not in activate_for_tasks/task_families", request.taskFamily))
	}
	if request.risk != nil {
		riskClasses := map[string]bool{}
		for _, risk := range asStrings(route["activate_for_risk_classes"]) {
			riskClasses[normalize(risk)] = true
		}
		if !riskClasses["all"] && !riskClasses[normalize(*request.risk)] {
			failures = append(failures, fmt.Sprintf("risk class '%s' not in activate_for_risk_classes", *request.risk))
		}
	}
	return failures
}

func selectConcepts(corpus *corpus, request retrievalRequest) *selection {
	roleBundle := corpus.roleBundles[request.role]
	taskBundle := corpus.taskBundles[request.taskFamily]
	alwaysLoad := asStrings(asObject(corpus.routing["always_load"])["concepts"])
	roleConcepts := map[string]bool{}
	for _, id := range append(asStrings(roleBundle["core_concepts"]), asStrings(roleBundle["default_concepts"])...) {
		roleConcepts[id] = true
	}
	var baseline []string
	for _, id := range asStrings(taskBundle["primary_concepts"]) {
		if roleConcepts[id] {
			baseline = append(baseline, id)
		}
	}
	sort.Strings(baseline)
	protected := map[string]bool{}
	for _, id := range append(append([]string{}, alwaysLoad...), baseline...) {
		protected[id] = true
	}

	nominations := map[string][]string{}
	nominate := func(id, source string) {
		if corpus.routes[id] == nil {
			return
		}
		nominations[id] = addUnique(nominations[id], source)
	}
	for _, id := range alwaysLoad {
		nominate(id, "always-load core concept")
	}
	for _, id := range baseline {
		nominate(id, "role bundle intersected with task bundle")
	}
	ids := make([]string, 0, len(corpus.routes))
	for id := range corpus.routes {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	for _, id := range ids {
		route := corpus.routes[id]
		for _, term := range asStrings(corpus.concepts[id]["retrieval_terms"]) {
			if phraseInText(term, request.question) {
				nominate(id, fmt.Sprintf("question term '%s'", term))
				break
			}
		}
		for _, variant := range asStrings(route["activate_for_tasks"]) {
			if contains(request.taskVariants, variant) {
				nominate(id, fmt.Sprintf("task variant '%s'", variant))
				break
			}
		}
		for _, condition := range asStrings(route["activate_for_repository_signals"]) {
			if signal, ok := matchingSignal(condition, request.signals); ok {
				nominate(id, fmt.Sprintf("signal '%s' matched activation signal '%s'", signal, condition))
				break
			}
		}
	}
	requestedLanguages := map[string]bool{}
	for _, language := range request.languages {
		requestedLanguages[normalize(language)] = true
	}
	for _, bundle := range asObjects(corpus.routing["language_bundles"]) {
		language := asString(bundle["language"])
		if requestedLanguages[normalize(language)] {
			for _, id := range asStrings(bundle["concepts"]) {
				nominate(id, fmt.Sprintf("language bundle '%s'", language))
			}
		}
	}
	if request.risk != nil {
		for _, route := range asObjects(corpus.routing["risk_routes"]) {
			if normalize(asString(route["risk_class"])) == normalize(*request.risk) {
				for _, id := range asStrings(route["concepts"]) {
					nominate(id, fmt.Sprintf("risk route '%s'", asString(route["risk_class"])))
				}
			}
		}
	}

	result := &selection{
		activated:             map[string][]string{},
		excluded:              map[string]string{},
		excludedPrerequisites: map[string]bool{},
	}
	nominatedIDs := make([]string, 0, len(nominations))
	for id := range nominations {
		nominatedIDs = append(nominatedIDs, id)
	}
	sort.Strings(nominatedIDs)
	for _, id := range nominatedIDs {
		route := corpus.routes[id]
		var failures []string
		if !protected[id] {
			failures = append(failures, additionalGateFailures(route, request, nominations[id])...)
		}
		if failure := languageGateFailure(route, request.languages); failure != "" {
			failures = append(failures, failure)
		}
		if failure := exclusionFailure(route, request.signals); failure != "" {
			failures = append(failures, failure)
		}
		if len(failures) > 0 {
			result.excluded[id] = "nominated by: " + strings.Join(nominations[id], "; ") + "; dropped: " + strings.Join(failures, "; ")
		} else {
			result.activated[id] = nominations[id]
		}
	}
	expandPrerequisites(corpus, result, request.signals, request.languages)
	return result
}

func expandPrerequisites(corpus *corpus, selected *selection, signals, languages []string) {
	queue := make([]string, 0, len(selected.activated))
	for id := range selected.activated {
		queue = append(queue, id)
	}
	sort.Strings(queue)
	processed := map[string]bool{}
	for len(queue) > 0 {
		id := queue[0]
		queue = queue[1:]
		if processed[id] {
			continue
		}
		processed[id] = true
		for _, prerequisite := range asStrings(corpus.routes[id]["prerequisites"]) {
			if corpus.concepts[prerequisite] == nil || selected.activated[prerequisite] != nil {
				continue
			}
			route := corpus.routes[prerequisite]
			var failures []string
			if failure := languageGateFailure(route, languages); failure != "" {
				failures = append(failures, failure)
			}
			if failure := exclusionFailure(route, signals); failure != "" {
				failures = append(failures, failure)
			}
			if len(failures) > 0 {
				selected.excluded[prerequisite] = fmt.Sprintf("nominated by: prerequisite of %s; dropped: %s", id, strings.Join(failures, "; "))
				selected.excludedPrerequisites[fmt.Sprintf("%s (prerequisite concept excluded) — required by %s", prerequisite, id)] = true
			} else {
				delete(selected.excluded, prerequisite)
				selected.activated[prerequisite] = []string{fmt.Sprintf("prerequisite of %s", id)}
				queue = append(queue, prerequisite)
			}
		}
	}
}

func applyRetrievalBudget(corpus *corpus, selected *selection, requested int) ([]string, object, []object, error) {
	active := map[string]bool{}
	for id := range selected.activated {
		active[id] = true
	}
	closure := func(start string) map[string]bool {
		result := map[string]bool{}
		queue := []string{start}
		for len(queue) > 0 {
			current := queue[len(queue)-1]
			queue = queue[:len(queue)-1]
			if result[current] || !active[current] {
				continue
			}
			result[current] = true
			for _, prerequisite := range asStrings(corpus.routes[current]["prerequisites"]) {
				if corpus.concepts[prerequisite] != nil {
					queue = append(queue, prerequisite)
				}
			}
		}
		return result
	}
	cost := func(ids map[string]bool) int {
		total := 0
		for id := range ids {
			total += asInt(corpus.routes[id]["retrieval_budget_hint"])
		}
		return total
	}
	mandatory := map[string]bool{}
	for _, id := range asStrings(asObject(corpus.routing["always_load"])["concepts"]) {
		for required := range closure(id) {
			mandatory[required] = true
		}
	}
	minimum := cost(mandatory)
	if requested < minimum {
		return nil, nil, nil, fmt.Errorf("retrieval budget %d is below mandatory core cost %d", requested, minimum)
	}
	chosen := map[string]bool{}
	for id := range mandatory {
		chosen[id] = true
	}
	used := minimum
	priorityRank := map[string]int{"core": 0, "high": 1, "normal": 2, "specialist": 3}
	var candidates []string
	for id := range active {
		if !mandatory[id] {
			candidates = append(candidates, id)
		}
	}
	sort.Slice(candidates, func(i, j int) bool {
		key := func(id string) [4]string {
			contextual := false
			baseline := false
			for _, reason := range selected.activated[id] {
				if strings.HasPrefix(reason, "question term") || strings.HasPrefix(reason, "signal ") || strings.HasPrefix(reason, "task variant") || strings.HasPrefix(reason, "language bundle") || strings.HasPrefix(reason, "risk route") {
					contextual = true
				}
				if reason == "role bundle intersected with task bundle" {
					baseline = true
				}
			}
			nomination := 2
			if contextual {
				nomination = 0
			} else if baseline {
				nomination = 1
			}
			route := corpus.routes[id]
			priority := priorityRank[optionalString(route["retrieval_priority"])]
			return [4]string{fmt.Sprintf("%02d", nomination), fmt.Sprintf("%02d", priority), fmt.Sprintf("%012d", asInt(route["retrieval_budget_hint"])), id}
		}
		left, right := key(candidates[i]), key(candidates[j])
		for index := 0; index < len(left); index++ {
			if left[index] != right[index] {
				return left[index] < right[index]
			}
		}
		return false
	})
	budgetExcluded := make([]object, 0)
	for _, id := range candidates {
		required := closure(id)
		for existing := range chosen {
			delete(required, existing)
		}
		requiredCost := cost(required)
		if used+requiredCost <= requested {
			for needed := range required {
				chosen[needed] = true
			}
			used += requiredCost
		} else {
			budgetExcluded = append(budgetExcluded, object{
				"id":     id,
				"cost":   requiredCost,
				"reason": fmt.Sprintf("requires %d relative routing-cost units with prerequisites; only %d remain", requiredCost, requested-used),
			})
		}
	}
	for id := range active {
		if !chosen[id] {
			delete(selected.activated, id)
		}
	}
	ordered := make([]string, 0, len(selected.activated))
	for id := range selected.activated {
		ordered = append(ordered, id)
	}
	sort.Slice(ordered, func(i, j int) bool {
		left, right := corpus.routes[ordered[i]], corpus.routes[ordered[j]]
		leftCore := optionalString(left["retrieval_priority"]) == "core"
		rightCore := optionalString(right["retrieval_priority"]) == "core"
		if leftCore != rightCore {
			return leftCore
		}
		leftCost, rightCost := asInt(left["retrieval_budget_hint"]), asInt(right["retrieval_budget_hint"])
		if leftCost != rightCost {
			return leftCost < rightCost
		}
		return ordered[i] < ordered[j]
	})
	filteredExcluded := budgetExcluded[:0]
	for _, record := range budgetExcluded {
		if !chosen[asString(record["id"])] {
			filteredExcluded = append(filteredExcluded, record)
		}
	}
	sort.Slice(filteredExcluded, func(i, j int) bool { return asString(filteredExcluded[i]["id"]) < asString(filteredExcluded[j]["id"]) })
	budget := object{
		"unit":             "relative-routing-cost-unit",
		"scope":            "activated-concept-selection-only",
		"meaning":          "Relative doctrine-selection cost; not a byte, word, or tokenizer-measured context limit. Delivery size is governed separately by the selected detail profile.",
		"requested":        requested,
		"minimum_required": minimum,
		"used":             used,
		"remaining":        requested - used,
	}
	return ordered, budget, filteredExcluded, nil
}
