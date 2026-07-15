package packet

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

type stringList []string

func (values *stringList) String() string { return strings.Join(*values, ",") }
func (values *stringList) Set(value string) error {
	*values = append(*values, value)
	return nil
}

func Run(arguments []string, retrieverVersion string, stdout, stderr io.Writer) int {
	options, code := parseOptions(arguments, stderr)
	if code < 0 {
		return 0
	}
	if code != 0 {
		return code
	}
	if !regexp.MustCompile(`^retriever-[0-9a-f]{16}$`).MatchString(retrieverVersion) {
		fmt.Fprintf(stderr, "invalid build retriever version %q; expected retriever- plus 16 lowercase hex characters\n", retrieverVersion)
		return 1
	}
	for _, field := range []struct {
		name   string
		values []string
	}{
		{"--task-variant", options.taskVariants},
		{"--lens", options.lenses},
		{"--signal", options.signals},
		{"--language", options.languages},
	} {
		for _, value := range field.values {
			if value == "" {
				fmt.Fprintf(stderr, "ERROR: %s values must not be empty\n", field.name)
				return 1
			}
		}
	}
	indexPath := options.index
	if indexPath == "" {
		indexPath = os.Getenv("BOOKS_DOCTRINE_INDEX")
	}
	if indexPath == "" {
		indexPath = defaultIndexPath()
	}
	doctrineRoot, err := locateDoctrineRoot(options.doctrineRoot, indexPath)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	corpus, err := openCorpus(indexPath, options.detail == "full")
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	sourceFingerprint, err := computeSourceFingerprint(doctrineRoot)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	if sourceFingerprint != corpus.sourceFingerprint {
		fmt.Fprintf(stderr, "stale doctrine index: source fingerprint %s does not match compiled fingerprint %s; rebuild the index\n", sourceFingerprint, corpus.sourceFingerprint)
		return 1
	}
	role := corpus.roleAliases[options.role]
	if role == "" {
		fmt.Fprintf(stderr, "unknown role '%s'. valid roles: %s\n", options.role, strings.Join(sortedKeys(corpus.roleBundles), ", "))
		return 1
	}
	taskFamily := corpus.taskAliases[options.task]
	if taskFamily == "" {
		fmt.Fprintf(stderr, "unknown task '%s'. valid tasks: %s\n", options.task, strings.Join(sortedKeys(corpus.taskBundles), ", "))
		return 1
	}
	variants := sortedUnique(options.taskVariants)
	var unknownVariants []string
	for _, variant := range variants {
		if !corpus.taskVariants[taskFamily][variant] {
			unknownVariants = append(unknownVariants, variant)
		}
	}
	if len(unknownVariants) > 0 {
		valid := sortedKeys(corpus.taskVariants[taskFamily])
		fmt.Fprintf(stderr, "unknown task variant(s) for '%s': %s. valid variants: %s\n", taskFamily, strings.Join(unknownVariants, ", "), strings.Join(valid, ", "))
		return 1
	}
	lenses := sortedUnique(options.lenses)
	var unknownLenses []string
	for _, lens := range lenses {
		if corpus.lenses[lens] == nil {
			unknownLenses = append(unknownLenses, lens)
		}
	}
	if len(unknownLenses) > 0 {
		fmt.Fprintf(stderr, "unknown lens(es): %s\n", strings.Join(unknownLenses, ", "))
		return 1
	}
	allowedLenses := map[string]bool{}
	for _, lens := range asStrings(corpus.roleBundles[role]["context_lenses"]) {
		allowedLenses[lens] = true
	}
	var disallowed []string
	for _, lens := range lenses {
		if !allowedLenses[lens] {
			disallowed = append(disallowed, lens)
		}
	}
	if len(disallowed) > 0 {
		fmt.Fprintf(stderr, "lens(es) not applicable to role '%s': %s\n", role, strings.Join(disallowed, ", "))
		return 1
	}
	evidenceRecords, evidenceErrors := readEvidenceRecords(options.evidence, corpus)
	if len(evidenceErrors) > 0 {
		for _, message := range evidenceErrors {
			fmt.Fprintf(stderr, "invalid evidence: %s\n", message)
		}
		return 1
	}
	budget := options.budget
	if !options.budgetSet {
		budget = asInt(corpus.roleBundles[role]["initial_retrieval_budget_hint"])
	}
	if budget <= 0 {
		fmt.Fprintln(stderr, "retrieval budget must be positive")
		return 1
	}
	languages := sortedUnique(options.languages)
	if len(languages) == 0 {
		languages = []string{"language-independent"}
	}
	var risk *string
	if options.riskSet {
		value := options.risk
		risk = &value
	}
	request := retrievalRequest{
		requestedRole: options.role,
		role:          role,
		requestedTask: options.task,
		taskFamily:    taskFamily,
		taskVariants:  variants,
		requestedLens: lenses,
		question:      options.question,
		signals:       sortedUnique(options.signals),
		languages:     languages,
		risk:          risk,
		budget:        budget,
		detail:        options.detail,
	}
	assembled, err := assemblePacket(corpus, request, evidenceRecords, retrieverVersion)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	serialized, err := prettyJSON(assembled)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	if options.out != "" {
		if err := os.WriteFile(options.out, serialized, 0o644); err != nil {
			fmt.Fprintf(stderr, "write packet: %v\n", err)
			return 1
		}
	}
	switch options.render {
	case "json":
		_, err = stdout.Write(serialized)
	case "markdown":
		_, err = io.WriteString(stdout, renderMarkdown(corpus, assembled))
	case "none":
	}
	if err != nil {
		fmt.Fprintf(stderr, "write output: %v\n", err)
		return 1
	}
	return 0
}

type cliOptions struct {
	role, task, question                               string
	taskVariants, lenses, signals, evidence, languages stringList
	risk                                               string
	riskSet                                            bool
	budget                                             int
	budgetSet                                          bool
	detail, out, render, index, doctrineRoot           string
}

type trackedString struct {
	value *string
	set   *bool
}

func (option trackedString) String() string {
	if option.value == nil {
		return ""
	}
	return *option.value
}
func (option trackedString) Set(value string) error {
	*option.value = value
	*option.set = true
	return nil
}

type trackedInt struct {
	value *int
	set   *bool
}

func (option trackedInt) String() string {
	if option.value == nil {
		return "0"
	}
	return fmt.Sprintf("%d", *option.value)
}
func (option trackedInt) Set(value string) error {
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return err
	}
	*option.value = parsed
	*option.set = true
	return nil
}

func parseOptions(arguments []string, stderr io.Writer) (cliOptions, int) {
	var result cliOptions
	flags := flag.NewFlagSet("assemble-packet", flag.ContinueOnError)
	flags.SetOutput(stderr)
	flags.StringVar(&result.role, "role", "", "agent role ID from the routing index")
	flags.StringVar(&result.task, "task", "", "task ID from the routing index")
	flags.Var(&result.taskVariants, "task-variant", "fine-grained task variant (repeatable)")
	flags.Var(&result.lenses, "lens", "explicit context lens ID (repeatable)")
	flags.StringVar(&result.question, "question", "", "free-text decision question")
	flags.Var(&result.signals, "signal", "repository activation signal (repeatable)")
	flags.Var(&result.evidence, "evidence", "typed evidence-record/1 JSON file (repeatable)")
	flags.Var(&result.languages, "language", "repository language (repeatable)")
	flags.Var(trackedString{&result.risk, &result.riskSet}, "risk", "declared risk class")
	flags.Var(trackedInt{&result.budget, &result.budgetSet}, "budget", "relative routing-cost budget")
	flags.StringVar(&result.detail, "detail", "compact", "compact or full")
	flags.StringVar(&result.out, "out", "", "write packet JSON here")
	flags.StringVar(&result.render, "render", "markdown", "markdown, json, or none")
	flags.StringVar(&result.index, "index", "", "compiled doctrine SQLite index")
	flags.StringVar(&result.doctrineRoot, "doctrine-root", "", "authoritative doctrine YAML root for stale-index validation")
	if err := flags.Parse(arguments); err != nil {
		if errors.Is(err, flag.ErrHelp) {
			return result, -1
		}
		return result, 2
	}
	if flags.NArg() != 0 {
		fmt.Fprintf(stderr, "unexpected positional arguments: %s\n", strings.Join(flags.Args(), " "))
		return result, 2
	}
	var missing []string
	for name, value := range map[string]string{"role": result.role, "task": result.task, "question": result.question} {
		if value == "" {
			missing = append(missing, "--"+name)
		}
	}
	sort.Strings(missing)
	if len(missing) > 0 {
		fmt.Fprintf(stderr, "the following arguments are required: %s\n", strings.Join(missing, ", "))
		return result, 2
	}
	if result.detail != "compact" && result.detail != "full" {
		fmt.Fprintf(stderr, "invalid --detail %q; expected compact or full\n", result.detail)
		return result, 2
	}
	if result.render != "markdown" && result.render != "json" && result.render != "none" {
		fmt.Fprintf(stderr, "invalid --render %q; expected markdown, json, or none\n", result.render)
		return result, 2
	}
	return result, 0
}

func defaultIndexPath() string {
	candidates := []string{
		filepath.Join("doctrine", "runtime", "doctrine-index.sqlite3"),
		filepath.Join("runtime", "doctrine-index.sqlite3"),
	}
	for _, candidate := range candidates {
		if _, err := os.Stat(candidate); err == nil {
			return candidate
		}
	}
	return candidates[0]
}

func readEvidenceRecords(paths []string, corpus *corpus) ([]object, []string) {
	records := make([]object, 0)
	var errors []string
	seen := map[string]bool{}
	for _, path := range paths {
		raw, err := os.ReadFile(path)
		if err != nil {
			errors = append(errors, fmt.Sprintf("%s: unable to read evidence record: %v", path, err))
			continue
		}
		decoder := json.NewDecoder(strings.NewReader(string(raw)))
		decoder.UseNumber()
		var record object
		if err := decoder.Decode(&record); err != nil {
			errors = append(errors, fmt.Sprintf("%s: unable to read evidence record: %v", path, err))
			continue
		}
		var trailing any
		if err := decoder.Decode(&trailing); err != io.EOF {
			if err == nil {
				err = fmt.Errorf("multiple JSON values")
			}
			errors = append(errors, fmt.Sprintf("%s: unable to read evidence record: %v", path, err))
			continue
		}
		pathErrors := validateEvidenceRecord(record)
		class, _ := record["evidence_class"].(string)
		if class != "" && corpus.evidenceClasses[class] == nil {
			pathErrors = append(pathErrors, fmt.Sprintf("unknown evidence_class '%s'", class))
		}
		if len(pathErrors) > 0 {
			for _, message := range pathErrors {
				errors = append(errors, fmt.Sprintf("%s: %s", path, message))
			}
			continue
		}
		id := asString(record["id"])
		if seen[id] {
			errors = append(errors, fmt.Sprintf("%s: duplicate evidence record ID '%s'", path, id))
			continue
		}
		seen[id] = true
		records = append(records, record)
	}
	sort.Slice(records, func(i, j int) bool { return asString(records[i]["id"]) < asString(records[j]["id"]) })
	return records, errors
}

func validateEvidenceRecord(record object) []string {
	var errors []string
	allowed := map[string]bool{"schema_version": true, "id": true, "evidence_class": true, "summary": true, "provenance": true, "satisfies": true}
	for key := range record {
		if !allowed[key] {
			errors = append(errors, fmt.Sprintf("unexpected property %q", key))
		}
	}
	for _, required := range []string{"schema_version", "id", "evidence_class", "summary", "provenance"} {
		if record[required] == nil {
			errors = append(errors, fmt.Sprintf("%s is required", required))
		}
	}
	stringFields := map[string]string{}
	for _, field := range []string{"schema_version", "id", "evidence_class", "summary"} {
		if record[field] == nil {
			continue
		}
		value, ok := record[field].(string)
		if !ok {
			errors = append(errors, fmt.Sprintf("%s must be a string", field))
			continue
		}
		stringFields[field] = value
	}
	if schemaVersion, ok := stringFields["schema_version"]; ok && schemaVersion != "evidence-record/1" {
		errors = append(errors, "schema_version must equal evidence-record/1")
	}
	if id, ok := stringFields["id"]; ok && !regexp.MustCompile(`^[a-z0-9][a-z0-9-]*$`).MatchString(id) {
		errors = append(errors, "id does not match the evidence-record pattern")
	}
	if class, ok := stringFields["evidence_class"]; ok && !regexp.MustCompile(`^evidence-[a-z0-9-]+$`).MatchString(class) {
		errors = append(errors, "evidence_class does not match the evidence class pattern")
	}
	if summary, ok := stringFields["summary"]; ok && strings.TrimSpace(summary) == "" {
		errors = append(errors, "summary must be a non-empty string")
	}
	provenanceValues, ok := record["provenance"].([]any)
	if !ok || len(provenanceValues) == 0 {
		errors = append(errors, "provenance must contain at least one record")
	} else {
		for index, raw := range provenanceValues {
			entry, ok := raw.(map[string]any)
			if !ok {
				errors = append(errors, fmt.Sprintf("provenance.%d must be an object", index))
				continue
			}
			allowedEntry := map[string]bool{"locator": true, "method": true, "observed_at": true, "content_sha256": true}
			for key := range entry {
				if !allowedEntry[key] {
					errors = append(errors, fmt.Sprintf("provenance.%d has unexpected property %q", index, key))
				}
			}
			locator, locatorOK := entry["locator"].(string)
			if !locatorOK || strings.TrimSpace(locator) == "" {
				errors = append(errors, fmt.Sprintf("provenance.%d.locator is required", index))
			}
			if entry["method"] != nil {
				method, ok := entry["method"].(string)
				if !ok || strings.TrimSpace(method) == "" {
					errors = append(errors, fmt.Sprintf("provenance.%d.method must be a non-empty string", index))
				}
			}
			if entry["observed_at"] != nil {
				if _, ok := entry["observed_at"].(string); !ok {
					errors = append(errors, fmt.Sprintf("provenance.%d.observed_at must be a string", index))
				}
			}
			if entry["content_sha256"] != nil {
				hash, ok := entry["content_sha256"].(string)
				if !ok || !regexp.MustCompile(`^[0-9a-f]{64}$`).MatchString(hash) {
					errors = append(errors, fmt.Sprintf("provenance.%d.content_sha256 is invalid", index))
				}
			}
		}
	}
	if rawSatisfies, exists := record["satisfies"]; exists {
		values, ok := rawSatisfies.([]any)
		if !ok {
			errors = append(errors, "satisfies must be an array")
		} else {
			seen := map[string]bool{}
			for index, raw := range values {
				value, ok := raw.(string)
				if !ok || value == "" {
					errors = append(errors, fmt.Sprintf("satisfies.%d must be a non-empty string", index))
					continue
				}
				if seen[value] {
					errors = append(errors, "satisfies entries must be unique")
				}
				seen[value] = true
			}
		}
	}
	sort.Strings(errors)
	return errors
}
