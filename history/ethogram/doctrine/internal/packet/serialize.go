package packet

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
)

func canonicalJSON(value any) ([]byte, error) {
	var buffer bytes.Buffer
	encoder := json.NewEncoder(&buffer)
	encoder.SetEscapeHTML(false)
	if err := encoder.Encode(value); err != nil {
		return nil, err
	}
	encoded := bytes.TrimSuffix(buffer.Bytes(), []byte("\n"))
	return restoreLineSeparators(encoded), nil
}

func prettyJSON(value any) ([]byte, error) {
	var buffer bytes.Buffer
	encoder := json.NewEncoder(&buffer)
	encoder.SetEscapeHTML(false)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(value); err != nil {
		return nil, err
	}
	return restoreLineSeparators(buffer.Bytes()), nil
}

func restoreLineSeparators(encoded []byte) []byte {
	result := make([]byte, 0, len(encoded))
	for index := 0; index < len(encoded); {
		replacement := []byte(nil)
		width := 0
		if index+6 <= len(encoded) && encoded[index] == '\\' {
			preceding := 0
			for cursor := index - 1; cursor >= 0 && encoded[cursor] == '\\'; cursor-- {
				preceding++
			}
			if preceding%2 == 0 {
				switch string(encoded[index : index+6]) {
				case `\u2028`:
					replacement = []byte("\u2028")
					width = 6
				case `\u2029`:
					replacement = []byte("\u2029")
					width = 6
				}
			}
		}
		if replacement != nil {
			result = append(result, replacement...)
			index += width
			continue
		}
		result = append(result, encoded[index])
		index++
	}
	return result
}

func sha256Hex(value []byte) string {
	digest := sha256.Sum256(value)
	return hex.EncodeToString(digest[:])
}
