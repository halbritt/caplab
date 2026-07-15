package packet

import (
	"fmt"
	"sort"
	"strings"
)

func collectConflicts(corpus *corpus, activated map[string]bool) []string {
	conflicts := map[string]bool{}
	for id := range activated {
		for _, conflict := range asStrings(corpus.concepts[id]["conflicts"]) {
			conflicts[conflict] = true
		}
	}
	for _, edge := range corpus.edges {
		conflict := optionalString(edge["conflict_ref"])
		if conflict == "" {
			continue
		}
		if activated[optionalString(edge["from"])] || activated[optionalString(edge["to"])] {
			conflicts[conflict] = true
		}
	}
	return sortedKeys(conflicts)
}

func collectFormulations(corpus *corpus, activated map[string]bool) []string {
	nodeIDs := map[string]bool{}
	for _, node := range corpus.nodes {
		id := asString(node["id"])
		if activated[id] || intersects(activated, asStrings(node["doctrine_refs"])) {
			nodeIDs[id] = true
		}
	}
	formulations := map[string]bool{}
	for _, node := range corpus.nodes {
		if nodeIDs[asString(node["id"])] {
			for _, id := range asStrings(node["formulations"]) {
				formulations[id] = true
			}
		}
	}
	for _, formulation := range corpus.formulations {
		for _, mapping := range asObjects(formulation["mappings"]) {
			if nodeIDs[optionalString(mapping["node_id"])] {
				formulations[asString(formulation["id"])] = true
				break
			}
		}
	}
	return sortedKeys(formulations)
}

func canonicalLocator(locator string) string {
	if strings.Contains(locator, " :: ") {
		return locator
	}
	if index := strings.Index(locator, "#"); index >= 0 {
		return locator[:index] + " :: " + locator[index+1:]
	}
	return locator
}

func collectSourceLocators(corpus *corpus, activated map[string]bool, formulationIDs []string) []string {
	locators := map[string]bool{}
	for id := range activated {
		for _, support := range asObjects(corpus.concepts[id]["source_support"]) {
			locators[canonicalLocator(asString(support["locator"]))] = true
		}
	}
	wanted := map[string]bool{}
	for _, id := range formulationIDs {
		wanted[id] = true
	}
	for _, formulation := range corpus.formulations {
		if wanted[asString(formulation["id"])] {
			locators[canonicalLocator(asString(formulation["locator"]))] = true
		}
	}
	return sortedKeys(locators)
}

func collectProvenanceLinks(corpus *corpus, activatedIDs []string) []object {
	links := make([]object, 0, len(activatedIDs))
	for _, id := range activatedIDs {
		var support []object
		for _, record := range asObjects(corpus.concepts[id]["source_support"]) {
			support = append(support, object{
				"source_id":    asString(record["source_id"]),
				"relationship": asString(record["relationship"]),
				"locator":      canonicalLocator(asString(record["locator"])),
				"contribution": asString(record["contribution"]),
			})
		}
		sort.Slice(support, func(i, j int) bool {
			for _, field := range []string{"source_id", "locator", "relationship"} {
				left, right := asString(support[i][field]), asString(support[j][field])
				if left != right {
					return left < right
				}
			}
			return false
		})
		links = append(links, object{
			"concept_id":      id,
			"formulation_ids": append([]string{}, corpus.formulationsByConcept[id]...),
			"source_support":  support,
		})
	}
	return links
}

func activatedLenses(corpus *corpus, request retrievalRequest) ([]string, map[string][]string) {
	allowed := map[string]bool{}
	for _, id := range asStrings(corpus.roleBundles[request.role]["context_lenses"]) {
		allowed[id] = true
	}
	selected := map[string][]string{}
	for _, id := range request.requestedLens {
		selected[id] = []string{"explicit lens selection"}
	}
	for _, language := range request.languages {
		id := "lens-" + normalize(language)
		if allowed[id] && corpus.lenses[id] != nil {
			selected[id] = addUnique(selected[id], fmt.Sprintf("language '%s'", language))
		}
	}
	allowedIDs := sortedKeys(allowed)
	for _, id := range allowedIDs {
		for _, condition := range asStrings(corpus.lenses[id]["activation_evidence"]) {
			if signal, ok := matchingSignal(condition, request.signals); ok {
				selected[id] = addUnique(selected[id], fmt.Sprintf("signal '%s' matched lens evidence '%s'", signal, condition))
				break
			}
		}
	}
	ids := make([]string, 0, len(selected))
	for id := range selected {
		ids = append(ids, id)
		sort.Strings(selected[id])
	}
	sort.Strings(ids)
	return ids, selected
}

func activatedProhibitions(corpus *corpus, taskFamily string) []string {
	selected := map[string]bool{}
	for _, id := range coreProhibitions {
		if corpus.prohibitions[id] != nil {
			selected[id] = true
		}
	}
	taskWords := words(taskFamily)
	for id, record := range corpus.prohibitions {
		scopes := strings.Join(asStrings(record["applies_when"]), " ")
		if wordIntersection(taskWords, words(scopes)) {
			selected[id] = true
		}
	}
	return sortedKeys(selected)
}

func obligationRecords(corpus *corpus, activatedIDs, evidenceClassIDs []string, evidenceRecords []object, taskFamily string) []object {
	activated := map[string]bool{}
	for _, id := range activatedIDs {
		activated[id] = true
	}
	type obligation struct{ requiredBy, requirement string }
	obligations := map[obligation]bool{}
	for _, id := range activatedIDs {
		for _, prerequisite := range asStrings(corpus.routes[id]["prerequisites"]) {
			if corpus.concepts[prerequisite] == nil || !activated[prerequisite] {
				obligations[obligation{id, prerequisite}] = true
			}
		}
		for _, requirement := range asStrings(corpus.concepts[id]["required_evidence"]) {
			obligations[obligation{id, requirement}] = true
		}
	}
	for _, evidenceClass := range evidenceClassIDs {
		obligations[obligation{"task:" + taskFamily, evidenceClass}] = true
	}
	ordered := make([]obligation, 0, len(obligations))
	for item := range obligations {
		ordered = append(ordered, item)
	}
	sort.Slice(ordered, func(i, j int) bool {
		if ordered[i].requiredBy != ordered[j].requiredBy {
			return ordered[i].requiredBy < ordered[j].requiredBy
		}
		return ordered[i].requirement < ordered[j].requirement
	})
	result := make([]object, 0, len(ordered))
	for _, item := range ordered {
		matched := make([]string, 0)
		if corpus.concepts[item.requirement] == nil {
			for _, evidence := range evidenceRecords {
				satisfies := map[string]bool{}
				for _, claim := range asStrings(evidence["satisfies"]) {
					satisfies[normalize(claim)] = true
				}
				if satisfies[normalize(item.requirement)] || item.requirement == optionalString(evidence["evidence_class"]) {
					matched = append(matched, asString(evidence["id"]))
				}
			}
		}
		sort.Strings(matched)
		status := "missing"
		if len(matched) > 0 {
			status = "satisfied"
		}
		result = append(result, object{
			"obligation_id": "obl-" + digest16(item.requiredBy+"\x00"+item.requirement),
			"requirement":   item.requirement,
			"required_by":   item.requiredBy,
			"evidence_ids":  matched,
			"status":        status,
		})
	}
	return result
}

func assemblePacket(corpus *corpus, request retrievalRequest, evidenceRecords []object, retrieverVersion string) (object, error) {
	selected := selectConcepts(corpus, request)
	activatedIDs, budget, budgetExcluded, err := applyRetrievalBudget(corpus, selected, request.budget)
	if err != nil {
		return nil, err
	}
	if err := hydrateConcepts(corpus, activatedIDs); err != nil {
		return nil, err
	}
	activatedSet := map[string]bool{}
	for _, id := range activatedIDs {
		activatedSet[id] = true
	}
	lensIDs, lensReasons := activatedLenses(corpus, request)
	procedureSet := map[string]bool{}
	for _, id := range asStrings(corpus.taskBundles[request.taskFamily]["procedures"]) {
		procedureSet[id] = true
	}
	if corpus.procedures["proc-assess-authority-to-act"] != nil {
		procedureSet["proc-assess-authority-to-act"] = true
	}
	procedureIDs := sortedKeys(procedureSet)
	evidenceClassIDs := make([]string, 0)
	for _, id := range asStrings(corpus.taskBundles[request.taskFamily]["evidence"]) {
		if corpus.evidenceClasses[id] != nil {
			evidenceClassIDs = append(evidenceClassIDs, id)
		}
	}
	sort.Strings(evidenceClassIDs)
	roleDefaults := asObject(asObject(corpus.authority["role_defaults"])[request.role])
	authority := cloneObject(roleDefaults)
	authority["artifact"] = "authority-model.yaml"
	prohibitionIDs := activatedProhibitions(corpus, request.taskFamily)
	changeTypeIDs := make([]string, 0)
	for _, id := range asStrings(corpus.taskBundles[request.taskFamily]["change_types"]) {
		if corpus.changeTypes[id] != nil {
			changeTypeIDs = append(changeTypeIDs, id)
		}
	}
	sort.Strings(changeTypeIDs)
	doctrineArtifacts := sortedUnique(asStrings(asObject(corpus.routing["always_load"])["artifacts"]))
	obligations := obligationRecords(corpus, activatedIDs, evidenceClassIDs, evidenceRecords, request.taskFamily)

	var risk any
	if request.risk != nil {
		risk = *request.risk
	}
	context := object{
		"requested_role":   request.requestedRole,
		"canonical_role":   request.role,
		"requested_task":   request.requestedTask,
		"task_family":      request.taskFamily,
		"task_variants":    sortedUnique(request.taskVariants),
		"requested_lenses": sortedUnique(request.requestedLens),
		"signals":          sortedUnique(request.signals),
		"languages":        sortedUnique(request.languages),
		"risk_class":       risk,
		"detail":           request.detail,
		"evidence_ids":     evidenceIDs(evidenceRecords),
		"retrieval_budget": request.budget,
	}
	packet := object{
		"schema_version":            packetSchemaVersion,
		"question":                  request.question,
		"corpus_version":            corpus.corpusVersion,
		"doctrine_version":          corpus.doctrineVersion,
		"retriever_version":         retrieverVersion,
		"retrieval_context":         context,
		"retrieval_budget":          budget,
		"budget_excluded":           budgetExcluded,
		"activated_concepts":        activatedIDs,
		"activated_procedures":      procedureIDs,
		"activated_lenses":          lensIDs,
		"activated_prohibitions":    prohibitionIDs,
		"required_evidence_classes": evidenceClassIDs,
		"authority_constraints":     authority,
		"applicable_change_types":   changeTypeIDs,
		"doctrine_artifacts":        doctrineArtifacts,
		"evidence_records":          evidenceRecords,
		"evidence_obligations":      obligations,
		"activation_reasons":        activationReasons(activatedIDs, selected, lensIDs, lensReasons, procedureIDs, prohibitionIDs, evidenceClassIDs, changeTypeIDs, doctrineArtifacts, request.taskFamily),
		"provenance_links":          collectProvenanceLinks(corpus, activatedIDs),
		"conflicts":                 collectConflicts(corpus, activatedSet),
		"excluded_candidates":       excludedCandidates(selected),
	}
	if request.detail == "full" {
		formulationIDs := collectFormulations(corpus, activatedSet)
		missing := map[string]bool{}
		for _, record := range obligations {
			if asString(record["status"]) == "missing" {
				missing[fmt.Sprintf("%s — required by %s", asString(record["requirement"]), asString(record["required_by"]))] = true
			}
		}
		for item := range selected.excludedPrerequisites {
			if strings.Contains(item, "(prerequisite concept excluded)") {
				missing[item] = true
			}
		}
		packet["audit_views"] = object{
			"formulations":     formulationIDs,
			"missing_evidence": sortedKeys(missing),
			"source_locators":  collectSourceLocators(corpus, activatedSet, formulationIDs),
		}
	}
	return contentAddressPacket(packet)
}

func contentAddressPacket(packet object) (object, error) {
	canonical, err := canonicalJSON(packet)
	if err != nil {
		return nil, err
	}
	digest := sha256Hex(canonical)
	packet["packet_content_sha256"] = digest
	packet["packet_id"] = "pkt-" + digest[:16]
	return packet, nil
}

func activationReasons(activatedIDs []string, selected *selection, lensIDs []string, lensReasons map[string][]string, procedureIDs, prohibitionIDs, evidenceClassIDs, changeTypeIDs, artifacts []string, taskFamily string) []object {
	var result []object
	for _, id := range activatedIDs {
		reasons := append([]string(nil), selected.activated[id]...)
		sort.Strings(reasons)
		result = append(result, object{"id": id, "reasons": reasons})
	}
	for _, id := range lensIDs {
		reasons := append([]string(nil), lensReasons[id]...)
		sort.Strings(reasons)
		result = append(result, object{"id": id, "reasons": reasons})
	}
	for _, id := range procedureIDs {
		result = append(result, object{"id": id, "reasons": []string{fmt.Sprintf("procedure for task family '%s'", taskFamily)}})
	}
	for _, id := range prohibitionIDs {
		reason := fmt.Sprintf("applies to task family '%s'", taskFamily)
		if contains(coreProhibitions, id) {
			reason = "core prohibition"
		}
		result = append(result, object{"id": id, "reasons": []string{reason}})
	}
	for _, id := range evidenceClassIDs {
		result = append(result, object{"id": id, "reasons": []string{fmt.Sprintf("required by task family '%s'", taskFamily)}})
	}
	for _, id := range changeTypeIDs {
		result = append(result, object{"id": id, "reasons": []string{fmt.Sprintf("applicable to task family '%s'", taskFamily)}})
	}
	for _, artifact := range artifacts {
		result = append(result, object{"id": artifact, "reasons": []string{"always-load doctrine artifact"}})
	}
	return result
}

func excludedCandidates(selected *selection) []object {
	ids := make([]string, 0, len(selected.excluded))
	for id := range selected.excluded {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	result := make([]object, 0, len(ids))
	for _, id := range ids {
		result = append(result, object{"id": id, "reason": selected.excluded[id]})
	}
	return result
}

func evidenceIDs(records []object) []string {
	result := make([]string, 0, len(records))
	for _, record := range records {
		result = append(result, asString(record["id"]))
	}
	return result
}

func sortedKeys[T any](values map[string]T) []string {
	result := make([]string, 0, len(values))
	for key := range values {
		result = append(result, key)
	}
	sort.Strings(result)
	return result
}

func intersects(set map[string]bool, values []string) bool {
	for _, value := range values {
		if set[value] {
			return true
		}
	}
	return false
}

func words(value string) map[string]bool {
	result := map[string]bool{}
	for _, word := range strings.Fields(strings.ReplaceAll(normalize(value), "-", " ")) {
		result[word] = true
	}
	return result
}

func wordIntersection(left, right map[string]bool) bool {
	for word := range left {
		if right[word] {
			return true
		}
	}
	return false
}
