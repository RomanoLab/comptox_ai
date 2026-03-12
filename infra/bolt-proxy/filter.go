package main

import (
	"regexp"
	"strings"
)

// writeKeywords lists Cypher keywords that indicate a write operation.
var writeKeywords = []string{
	"CREATE",
	"MERGE",
	"SET",
	"DELETE",
	"REMOVE",
	"DROP",
	"DETACH",
	"LOAD",
}

// stripComments removes single-line (//) and block (/* */) Cypher comments.
var blockCommentRe = regexp.MustCompile(`(?s)/\*.*?\*/`)
var lineCommentRe = regexp.MustCompile(`//[^\n]*`)

func stripComments(query string) string {
	query = blockCommentRe.ReplaceAllString(query, "")
	query = lineCommentRe.ReplaceAllString(query, "")
	return query
}

// isWriteQuery returns true if the Cypher query appears to perform a write operation.
// It uses a conservative approach: if the query cannot be parsed, it is blocked.
func isWriteQuery(query string) bool {
	cleaned := strings.TrimSpace(stripComments(query))
	if cleaned == "" {
		return true // empty/unparseable → block
	}

	upper := strings.ToUpper(cleaned)

	// Extract the first keyword (split on whitespace or opening paren)
	fields := strings.Fields(upper)
	if len(fields) == 0 {
		return true
	}
	firstWord := fields[0]

	// Check against write keywords
	for _, kw := range writeKeywords {
		if firstWord == kw {
			return true
		}
	}

	// Block CALL for write procedures but allow known read-only CALL targets
	if firstWord == "CALL" {
		return isWriteCall(upper)
	}

	return false
}

// isWriteCall checks whether a CALL statement invokes a write procedure.
// Known read-only procedure prefixes are allowed through.
var readOnlyCallPrefixes = []string{
	"CALL DB.",
	"CALL SCHEMA.",
	"CALL MG.",
}

func isWriteCall(upperQuery string) bool {
	for _, prefix := range readOnlyCallPrefixes {
		if strings.HasPrefix(upperQuery, prefix) {
			return false
		}
	}
	// Unknown CALL → block
	return true
}
