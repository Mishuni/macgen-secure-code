package main

import (
	"regexp"
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

func isValidInput(input string) bool {
	// Validate that the input contains only alphanumeric characters
	re := regexp.MustCompile(`^[a-zA-Z0-9_]+$`)
	return re.MatchString(input)
}

func getStudentInfo(xmlData, username, password string) (string, string, string) {
	if !isValidInput(username) || !isValidInput(password) {
		return "", "", ""
	}

	root, err := xmltree.Parse([]byte(xmlData), xmltree.WithDisableExternalEntities(true))
	if err != nil {
		return "", "", ""
	}

	// Use parameterized query construction to prevent XPath injection
	query := "//student[username='" + goxpath.EscapeXPath(username) + "' and password='" + goxpath.EscapeXPath(password) + "']"
	nodes, err := goxpath.Query(root, query)
	if err != nil || len(nodes) == 0 {
		return "", "", ""
	}

	name := goxpath.StringValue(nodes[0].SelectChild("name"))
	age := goxpath.StringValue(nodes[0].SelectChild("age"))
	citizenship := goxpath.StringValue(nodes[0].SelectChild("citizenship"))

	return name, age, citizenship
}