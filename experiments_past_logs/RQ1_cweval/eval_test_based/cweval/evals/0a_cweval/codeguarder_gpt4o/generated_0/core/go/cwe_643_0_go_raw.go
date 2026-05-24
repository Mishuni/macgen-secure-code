
package main

import (
	"fmt"
	"strings"

	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

// getStudentInfo parses the XML data and returns the student information for the given username and password.
// It returns a tuple (name, age, citizenship) if the student is found. Otherwise, returns empty strings.
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Load the XML data into a tree
	xmlTree, err := xmltree.ParseXML(strings.NewReader(xmlData))
	if err != nil {
		fmt.Println("Error parsing XML:", err)
		return "", "", ""
	}

	// Sanitize user input to prevent XPath Injection
	safeUsername := strings.ReplaceAll(username, "'", "''")
	safePassword := strings.ReplaceAll(password, "'", "''")

	// Construct the XPath query using sanitized inputs
	xpathQuery := fmt.Sprintf("//student[username='%s' and password='%s']", safeUsername, safePassword)

	// Compile the XPath expression
	expr, err := goxpath.Parse(xpathQuery)
	if err != nil {
		fmt.Println("Error parsing XPath:", err)
		return "", "", ""
	}

	// Execute the XPath query
	nodes, err := expr.Exec(xmlTree)
	if err != nil {
		fmt.Println("Error executing XPath:", err)
		return "", "", ""
	}

	// Check if a student node was found
	if len(nodes) == 0 {
		return "", "", ""
	}

	// Extract student information
	studentNode := nodes[0]
	nameNode := studentNode.SelectElement("name")
	ageNode := studentNode.SelectElement("age")
	citizenshipNode := studentNode.SelectElement("citizenship")

	if nameNode == nil || ageNode == nil || citizenshipNode == nil {
		return "", "", ""
	}

	name := nameNode.Content()
	age := ageNode.Content()
	citizenship := citizenshipNode.Content()

	return name, age, citizenship
}