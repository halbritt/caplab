package packet

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"strconv"
	"strings"
	"unicode"
)

const packetSchemaVersion = "evidence-packet/2"

var coreProhibitions = []string{
	"prohibit-generic-doctrine-over-local-contract",
	"prohibit-authority-inference-from-access",
}

type object map[string]any

type corpus struct {
	routing               object
	routes                map[string]object
	roleBundles           map[string]object
	taskBundles           map[string]object
	roleAliases           map[string]string
	taskAliases           map[string]string
	taskVariants          map[string]map[string]bool
	concepts              map[string]object
	conceptJSON           map[string]string
	conflicts             map[string]object
	nodes                 []object
	formulations          []object
	formulationsByConcept map[string][]string
	edges                 []object
	procedures            map[string]object
	lenses                map[string]object
	prohibitions          map[string]object
	evidenceClasses       map[string]object
	authority             object
	changeTypes           map[string]object
	corpusVersion         string
	doctrineVersion       string
	indexHash             string
	sourceFingerprint     string
}

type retrievalRequest struct {
	requestedRole string
	role          string
	requestedTask string
	taskFamily    string
	taskVariants  []string
	requestedLens []string
	question      string
	signals       []string
	languages     []string
	risk          *string
	budget        int
	detail        string
}

type selection struct {
	activated             map[string][]string
	excluded              map[string]string
	excludedPrerequisites map[string]bool
}

func asObject(value any) object {
	if value == nil {
		return object{}
	}
	if result, ok := value.(map[string]any); ok {
		return result
	}
	if result, ok := value.(object); ok {
		return result
	}
	panic(fmt.Sprintf("expected object, got %T", value))
}

func asObjects(value any) []object {
	if value == nil {
		return nil
	}
	values, ok := value.([]any)
	if !ok {
		if objects, ok := value.([]object); ok {
			return objects
		}
		panic(fmt.Sprintf("expected object array, got %T", value))
	}
	result := make([]object, 0, len(values))
	for _, item := range values {
		result = append(result, asObject(item))
	}
	return result
}

func asStrings(value any) []string {
	if value == nil {
		return nil
	}
	if result, ok := value.([]string); ok {
		return append([]string(nil), result...)
	}
	values, ok := value.([]any)
	if !ok {
		panic(fmt.Sprintf("expected string array, got %T", value))
	}
	result := make([]string, 0, len(values))
	for _, item := range values {
		result = append(result, asString(item))
	}
	return result
}

func asString(value any) string {
	switch typed := value.(type) {
	case string:
		return typed
	case json.Number:
		return typed.String()
	default:
		panic(fmt.Sprintf("expected string, got %T", value))
	}
}

func optionalString(value any) string {
	if value == nil {
		return ""
	}
	return asString(value)
}

func asInt(value any) int {
	switch typed := value.(type) {
	case int:
		return typed
	case int64:
		return int(typed)
	case float64:
		return int(typed)
	case json.Number:
		result, err := strconv.Atoi(typed.String())
		if err != nil {
			panic(err)
		}
		return result
	default:
		panic(fmt.Sprintf("expected integer, got %T", value))
	}
}

func cloneObject(source object) object {
	result := make(object, len(source))
	for key, value := range source {
		result[key] = value
	}
	return result
}

func sortedUnique(values []string) []string {
	seen := map[string]bool{}
	for _, value := range values {
		seen[value] = true
	}
	result := make([]string, 0, len(seen))
	for value := range seen {
		result = append(result, value)
	}
	sort.Strings(result)
	return result
}

func contains(values []string, wanted string) bool {
	for _, value := range values {
		if value == wanted {
			return true
		}
	}
	return false
}

func addUnique(values []string, value string) []string {
	if contains(values, value) {
		return values
	}
	return append(values, value)
}

func digest16(value string) string {
	digest := sha256.Sum256([]byte(value))
	return hex.EncodeToString(digest[:])[:16]
}

func normalize(value string) string {
	var lowered strings.Builder
	for _, runeValue := range value {
		if runeValue == '\u0130' {
			// Python's str.lower follows Unicode SpecialCasing for capital I
			// with dot, expanding it to i plus a combining dot.
			lowered.WriteString("i\u0307")
			continue
		}
		lowered.WriteRune(unicode.ToLower(runeValue))
	}
	fields := strings.FieldsFunc(lowered.String(), func(runeValue rune) bool {
		return unicode.IsSpace(runeValue) || (runeValue >= '\u001c' && runeValue <= '\u001f')
	})
	return strings.Join(fields, " ")
}
