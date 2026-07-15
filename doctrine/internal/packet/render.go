package packet

import (
	"fmt"
	"sort"
	"strings"
)

const precedencePreamble = "Precedence: explicit human authorization and stop conditions, then accepted repository contracts, tests, decisions, and current runtime facts, precede all doctrine below. This packet is retrieved guidance: it can justify a question, investigation, proposal, or bounded action; retrieval never creates authority to select, execute, verify, or accept a change."

func renderMarkdown(corpus *corpus, packet object) string {
	context := asObject(packet["retrieval_context"])
	provenanceByConcept := map[string]object{}
	for _, record := range asObjects(packet["provenance_links"]) {
		provenanceByConcept[asString(record["concept_id"])] = record
	}
	var lines []string
	lines = append(lines, "# Doctrine evidence packet", "")
	lines = append(lines, fmt.Sprintf("- Packet: %s · Corpus: %s", asString(packet["packet_id"]), asString(packet["corpus_version"])))
	lines = append(lines, fmt.Sprintf("- Question: %s", asString(packet["question"])))
	contextLine := fmt.Sprintf("- Role: %s · Task: %s · Languages: %s", asString(context["canonical_role"]), asString(context["task_family"]), strings.Join(asStrings(context["languages"]), ", "))
	if context["risk_class"] != nil {
		contextLine += fmt.Sprintf(" · Risk: %s", asString(context["risk_class"]))
	}
	if signals := asStrings(context["signals"]); len(signals) > 0 {
		contextLine += " · Signals: " + strings.Join(signals, "; ")
	}
	lines = append(lines, contextLine)
	budget := asObject(packet["retrieval_budget"])
	lines = append(lines, fmt.Sprintf("- Detail: %s · Selection cost: %d/%d %s", asString(context["detail"]), asInt(budget["used"]), asInt(budget["requested"]), asString(budget["unit"])))
	lines = append(lines, "", precedencePreamble, "")

	activated := asStrings(packet["activated_concepts"])
	lines = append(lines, fmt.Sprintf("## Activated concepts (%d)", len(activated)))
	for _, id := range activated {
		concept := corpus.concepts[id]
		route := corpus.routes[id]
		priority := optionalString(route["retrieval_priority"])
		if priority == "" {
			priority = "normal"
		}
		lines = append(lines, "", fmt.Sprintf("### %s (%s)", id, priority))
		lines = append(lines, fmt.Sprintf("- Claim: %s", asString(concept["claim"])))
		lines = append(lines, fmt.Sprintf("- Decision rule: %s", asString(concept["decision_rule"])))
		var sourceRefs []string
		for _, support := range asObjects(provenanceByConcept[id]["source_support"]) {
			sourceRefs = append(sourceRefs, fmt.Sprintf("%s [%s] %s", asString(support["source_id"]), asString(support["relationship"]), asString(support["locator"])))
		}
		lines = append(lines, "- Source support: "+strings.Join(sourceRefs, "; "))
	}

	lines = append(lines, "", "## Operational layers")
	for _, entry := range []struct{ title, field string }{
		{"Procedures", "activated_procedures"},
		{"Lenses", "activated_lenses"},
		{"Prohibitions", "activated_prohibitions"},
		{"Evidence classes", "required_evidence_classes"},
		{"Change types", "applicable_change_types"},
	} {
		values := asStrings(packet[entry.field])
		joined := "none"
		if len(values) > 0 {
			joined = strings.Join(values, ", ")
		}
		lines = append(lines, fmt.Sprintf("- %s: %s", entry.title, joined))
	}
	authority := asObject(packet["authority_constraints"])
	lines = append(lines, fmt.Sprintf("- Authority ceiling: %s", asString(authority["usual_ceiling"])))
	for _, constraint := range asStrings(authority["constraints"]) {
		lines = append(lines, "  - "+constraint)
	}

	reasons := asObjects(packet["activation_reasons"])
	lines = append(lines, "", fmt.Sprintf("## Activation reasons (%d)", len(reasons)))
	for _, record := range reasons {
		lines = append(lines, fmt.Sprintf("- %s: %s", asString(record["id"]), strings.Join(asStrings(record["reasons"]), "; ")))
	}
	var missing []object
	for _, record := range asObjects(packet["evidence_obligations"]) {
		if asString(record["status"]) == "missing" {
			missing = append(missing, record)
		}
	}
	lines = append(lines, "", fmt.Sprintf("## Unmet evidence obligations (%d)", len(missing)))
	for _, record := range missing {
		lines = append(lines, fmt.Sprintf("- %s: %s", asString(record["required_by"]), asString(record["requirement"])))
	}
	conflicts := asStrings(packet["conflicts"])
	lines = append(lines, "", fmt.Sprintf("## Conflicts (%d)", len(conflicts)))
	for _, id := range conflicts {
		lines = append(lines, "- "+id)
	}
	if rawAudit, ok := packet["audit_views"]; ok {
		audit := asObject(rawAudit)
		lines = append(lines, "", "## Expanded audit views")
		for _, entry := range []struct{ title, field string }{
			{"Formulations", "formulations"},
			{"Missing evidence", "missing_evidence"},
			{"Source locators", "source_locators"},
		} {
			values := asStrings(audit[entry.field])
			sort.Strings(values)
			lines = append(lines, "", fmt.Sprintf("### %s (%d)", entry.title, len(values)))
			for _, value := range values {
				lines = append(lines, "- "+value)
			}
		}
	}
	return strings.Join(append(lines, ""), "\n")
}
