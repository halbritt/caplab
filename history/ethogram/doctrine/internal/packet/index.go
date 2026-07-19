package packet

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/url"
	"os"
	"path/filepath"
	"sort"
	"strings"

	_ "modernc.org/sqlite"
)

func decodeObject(raw string) (object, error) {
	decoder := json.NewDecoder(strings.NewReader(raw))
	decoder.UseNumber()
	var result object
	if err := decoder.Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}

func openCorpus(path string, fullDetail bool) (*corpus, error) {
	absolute, err := filepath.Abs(path)
	if err != nil {
		return nil, err
	}
	if err := verifyIndexFileHash(absolute); err != nil {
		return nil, err
	}
	dsn := (&url.URL{
		Scheme:   "file",
		Path:     filepath.ToSlash(absolute),
		RawQuery: "mode=ro&immutable=1",
	}).String()
	database, err := sql.Open("sqlite", dsn)
	if err != nil {
		return nil, fmt.Errorf("open doctrine index: %w", err)
	}
	defer database.Close()
	if err := database.Ping(); err != nil {
		return nil, fmt.Errorf("open doctrine index %s: %w", path, err)
	}

	meta, err := loadMeta(database)
	if err != nil {
		return nil, err
	}
	if meta["index_schema_version"] != "doctrine-index/1" {
		return nil, fmt.Errorf("unsupported doctrine index schema %q", meta["index_schema_version"])
	}
	for _, key := range []string{"corpus_version", "doctrine_version", "index_content_hash", "source_fingerprint"} {
		if meta[key] == "" {
			return nil, fmt.Errorf("doctrine index metadata is missing %s", key)
		}
	}
	if decoded, err := hex.DecodeString(meta["index_content_hash"]); err != nil || len(decoded) != sha256.Size {
		return nil, fmt.Errorf("doctrine index content hash is malformed")
	}
	documents, err := loadDocuments(database)
	if err != nil {
		return nil, err
	}
	concepts, conceptJSON, err := loadConceptSelectionData(database)
	if err != nil {
		return nil, err
	}
	nodes := make([]object, 0)
	formulations := make([]object, 0)
	if fullDetail {
		nodes, err = loadObjectList(database, "SELECT node_json FROM nodes ORDER BY node_id")
		if err != nil {
			return nil, err
		}
		formulations, err = loadObjectList(database, "SELECT formulation_json FROM formulations ORDER BY formulation_id")
		if err != nil {
			return nil, err
		}
	}
	formulationsByConcept, err := loadFormulationMappings(database)
	if err != nil {
		return nil, err
	}
	edges, err := loadConflictEdges(database)
	if err != nil {
		return nil, err
	}

	routing := documents["routing-index.yaml"]
	if routing == nil {
		return nil, fmt.Errorf("doctrine index is missing routing-index.yaml")
	}
	result := &corpus{
		routing:               routing,
		routes:                objectMap(asObjects(routing["concept_routes"]), "concept_id"),
		roleBundles:           objectMap(asObjects(routing["role_bundles"]), "role"),
		taskBundles:           objectMap(asObjects(routing["task_bundles"]), "task"),
		roleAliases:           map[string]string{},
		taskAliases:           map[string]string{},
		taskVariants:          map[string]map[string]bool{},
		concepts:              concepts,
		conceptJSON:           conceptJSON,
		conflicts:             objectMap(asObjects(documents["conflicts.yaml"]["conflicts"]), "conflict_id"),
		nodes:                 nodes,
		formulations:          formulations,
		formulationsByConcept: formulationsByConcept,
		edges:                 edges,
		procedures:            objectMap(asObjects(documents["procedures.yaml"]["procedures"]), "id"),
		lenses:                objectMap(asObjects(documents["context-lenses.yaml"]["lenses"]), "id"),
		prohibitions:          objectMap(asObjects(documents["negative-doctrine.yaml"]["prohibitions"]), "id"),
		evidenceClasses:       objectMap(asObjects(documents["evidence-taxonomy.yaml"]["classes"]), "id"),
		authority:             documents["authority-model.yaml"],
		changeTypes:           objectMap(asObjects(documents["change-types.yaml"]["types"]), "id"),
		corpusVersion:         meta["corpus_version"],
		doctrineVersion:       meta["doctrine_version"],
		indexHash:             meta["index_content_hash"],
		sourceFingerprint:     meta["source_fingerprint"],
	}
	for _, record := range asObjects(routing["role_registry"]) {
		role := asString(record["role"])
		for _, alias := range append([]string{role}, asStrings(record["aliases"])...) {
			result.roleAliases[alias] = role
		}
	}
	for _, record := range asObjects(routing["task_registry"]) {
		family := asString(record["family"])
		for _, alias := range append([]string{family}, asStrings(record["aliases"])...) {
			result.taskAliases[alias] = family
		}
		variants := map[string]bool{}
		for _, variant := range asStrings(record["variants"]) {
			variants[variant] = true
		}
		result.taskVariants[family] = variants
	}
	return result, nil
}

func loadConceptSelectionData(database *sql.DB) (map[string]object, map[string]string, error) {
	rows, err := database.Query("SELECT concept_id, retrieval_terms_json, concept_json FROM concepts ORDER BY concept_id")
	if err != nil {
		return nil, nil, fmt.Errorf("read doctrine concept selection data: %w", err)
	}
	defer rows.Close()
	concepts := map[string]object{}
	rawConcepts := map[string]string{}
	for rows.Next() {
		var id, rawTerms, rawConcept string
		if err := rows.Scan(&id, &rawTerms, &rawConcept); err != nil {
			return nil, nil, err
		}
		var terms []string
		if err := json.Unmarshal([]byte(rawTerms), &terms); err != nil {
			return nil, nil, fmt.Errorf("decode retrieval terms for %s: %w", id, err)
		}
		concepts[id] = object{"id": id, "retrieval_terms": terms}
		rawConcepts[id] = rawConcept
	}
	if err := rows.Err(); err != nil {
		return nil, nil, err
	}
	return concepts, rawConcepts, nil
}

func hydrateConcepts(corpus *corpus, ids []string) error {
	for _, id := range ids {
		raw, ok := corpus.conceptJSON[id]
		if !ok {
			return fmt.Errorf("doctrine index is missing concept %s", id)
		}
		concept, err := decodeObject(raw)
		if err != nil {
			return fmt.Errorf("decode doctrine concept %s: %w", id, err)
		}
		corpus.concepts[id] = concept
	}
	return nil
}

func loadConflictEdges(database *sql.DB) ([]object, error) {
	rows, err := database.Query("SELECT from_node_id, to_node_id, conflict_ref FROM edges WHERE conflict_ref IS NOT NULL ORDER BY edge_id")
	if err != nil {
		return nil, fmt.Errorf("read doctrine conflict edges: %w", err)
	}
	defer rows.Close()
	result := make([]object, 0)
	for rows.Next() {
		var from, to, conflict string
		if err := rows.Scan(&from, &to, &conflict); err != nil {
			return nil, err
		}
		result = append(result, object{"from": from, "to": to, "conflict_ref": conflict})
	}
	return result, rows.Err()
}

func verifyIndexFileHash(path string) error {
	checksumPath := path + ".sha256"
	raw, err := os.ReadFile(checksumPath)
	if err != nil {
		return fmt.Errorf("read doctrine index file hash %s: %w", checksumPath, err)
	}
	expected := strings.TrimSpace(string(raw))
	decoded, err := hex.DecodeString(expected)
	if err != nil || len(decoded) != sha256.Size {
		return fmt.Errorf("doctrine index file hash %s is malformed", checksumPath)
	}
	index, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("read doctrine index for file-hash verification: %w", err)
	}
	defer index.Close()
	digest := sha256.New()
	if _, err := io.Copy(digest, index); err != nil {
		return fmt.Errorf("hash doctrine index: %w", err)
	}
	actual := hex.EncodeToString(digest.Sum(nil))
	if actual != expected {
		return fmt.Errorf("doctrine index file content hash mismatch: got %s, expected %s", actual, expected)
	}
	return nil
}

func locateDoctrineRoot(explicitRoot, indexPath string) (string, error) {
	var candidates []string
	if explicitRoot != "" {
		candidates = append(candidates, explicitRoot)
	} else {
		workingDirectory, err := os.Getwd()
		if err == nil {
			candidates = append(candidates, filepath.Join(workingDirectory, "doctrine"), workingDirectory)
		}
		absoluteIndex, err := filepath.Abs(indexPath)
		if err == nil {
			indexDirectory := filepath.Dir(absoluteIndex)
			if filepath.Base(indexDirectory) == "runtime" {
				candidates = append(candidates, filepath.Dir(indexDirectory))
			}
		}
	}
	for _, candidate := range candidates {
		if _, err := os.Stat(filepath.Join(candidate, "routing-index.yaml")); err == nil {
			return filepath.Clean(candidate), nil
		}
	}
	if explicitRoot != "" {
		return "", fmt.Errorf("doctrine root %s does not contain routing-index.yaml", explicitRoot)
	}
	return "", fmt.Errorf("unable to locate authoritative doctrine YAML; pass --doctrine-root")
}

func computeSourceFingerprint(root string) (string, error) {
	paths := []string{
		"routing-index.yaml", "procedures.yaml", "context-lenses.yaml",
		"negative-doctrine.yaml", "conflicts.yaml", "evidence-taxonomy.yaml",
		"authority-model.yaml", "change-types.yaml",
		"runtime/evidence-packet.schema.json", "runtime/evidence-record.schema.json",
		"graph/nodes.yaml", "graph/formulations.yaml", "graph/edges.yaml",
		"sources.yaml", "traceability.yaml",
	}
	conceptPaths, err := filepath.Glob(filepath.Join(root, "concepts", "*.yaml"))
	if err != nil {
		return "", err
	}
	for _, path := range conceptPaths {
		relative, err := filepath.Rel(root, path)
		if err != nil {
			return "", err
		}
		paths = append(paths, filepath.ToSlash(relative))
	}
	sort.Strings(paths)
	digest := sha256.New()
	for _, relative := range paths {
		content, err := os.ReadFile(filepath.Join(root, filepath.FromSlash(relative)))
		if err != nil {
			return "", fmt.Errorf("read doctrine source %s: %w", relative, err)
		}
		contentDigest := sha256.Sum256(content)
		digest.Write([]byte(relative))
		digest.Write([]byte{0})
		digest.Write(contentDigest[:])
	}
	return hex.EncodeToString(digest.Sum(nil)), nil
}

func loadMeta(database *sql.DB) (map[string]string, error) {
	rows, err := database.Query("SELECT key, value FROM meta ORDER BY key")
	if err != nil {
		return nil, fmt.Errorf("read doctrine index metadata: %w", err)
	}
	defer rows.Close()
	result := map[string]string{}
	for rows.Next() {
		var key, value string
		if err := rows.Scan(&key, &value); err != nil {
			return nil, err
		}
		result[key] = value
	}
	return result, rows.Err()
}

func loadDocuments(database *sql.DB) (map[string]object, error) {
	return loadObjectTable(database, "SELECT document_key, document_json FROM documents WHERE document_key NOT IN ('sources.yaml', 'traceability.yaml') ORDER BY document_key")
}

func loadFormulationMappings(database *sql.DB) (map[string][]string, error) {
	rows, err := database.Query("SELECT formulation_id, node_id FROM formulation_mappings ORDER BY formulation_id, ordinal")
	if err != nil {
		return nil, fmt.Errorf("read doctrine formulation mappings: %w", err)
	}
	defer rows.Close()
	result := map[string][]string{}
	for rows.Next() {
		var formulationID, nodeID string
		if err := rows.Scan(&formulationID, &nodeID); err != nil {
			return nil, err
		}
		result[nodeID] = append(result[nodeID], formulationID)
	}
	return result, rows.Err()
}

func loadObjectTable(database *sql.DB, query string) (map[string]object, error) {
	rows, err := database.Query(query)
	if err != nil {
		return nil, fmt.Errorf("read doctrine index: %w", err)
	}
	defer rows.Close()
	result := map[string]object{}
	for rows.Next() {
		var key, raw string
		if err := rows.Scan(&key, &raw); err != nil {
			return nil, err
		}
		document, err := decodeObject(raw)
		if err != nil {
			return nil, fmt.Errorf("decode doctrine index row %s: %w", key, err)
		}
		result[key] = document
	}
	return result, rows.Err()
}

func loadObjectList(database *sql.DB, query string) ([]object, error) {
	rows, err := database.Query(query)
	if err != nil {
		return nil, fmt.Errorf("read doctrine index: %w", err)
	}
	defer rows.Close()
	var result []object
	for rows.Next() {
		var raw string
		if err := rows.Scan(&raw); err != nil {
			return nil, err
		}
		document, err := decodeObject(raw)
		if err != nil {
			return nil, fmt.Errorf("decode doctrine index row: %w", err)
		}
		result = append(result, document)
	}
	return result, rows.Err()
}

func objectMap(records []object, key string) map[string]object {
	result := make(map[string]object, len(records))
	for _, record := range records {
		result[asString(record[key])] = record
	}
	return result
}
