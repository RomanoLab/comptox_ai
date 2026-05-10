package main

import "testing"

func TestIsWriteQuery(t *testing.T) {
	cases := []struct {
		name  string
		query string
		want  bool
	}{
		{"plain match", "MATCH (n) RETURN n", false},
		{"match with where", "MATCH (n:Chemical) WHERE n.name = 'x' RETURN n", false},
		{"create", "CREATE (n:Chemical) RETURN n", true},
		{"merge", "MERGE (n:X) RETURN n", true},
		{"set", "SET n.x = 1", true},
		{"delete", "DELETE n", true},
		{"detach delete", "DETACH DELETE n", true},
		{"remove", "REMOVE n.x", true},
		{"drop", "DROP CONSTRAINT", true},
		{"load csv", "LOAD CSV FROM 'x' AS row CREATE (n) RETURN n", true},
		{"call db.labels", "CALL db.labels()", false},
		{"call mg.labels", "CALL mg.labels()", false},
		{"call schema.node_type_properties", "CALL schema.node_type_properties()", false},
		{"call write proc", "CALL apoc.create.node(['X'], {})", true},
		{"empty", "", true},
		{"only comments", "// nothing here", true},
		{"comment then match", "// returns nodes\nMATCH (n) RETURN n", false},
		{"block comment match", "/* hi */ MATCH (n) RETURN n", false},
		{"lowercase create", "create (n) return n", true},
		{"leading whitespace match", "   \n  MATCH (n) RETURN n", false},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := isWriteQuery(tc.query)
			if got != tc.want {
				t.Fatalf("isWriteQuery(%q) = %v, want %v", tc.query, got, tc.want)
			}
		})
	}
}
