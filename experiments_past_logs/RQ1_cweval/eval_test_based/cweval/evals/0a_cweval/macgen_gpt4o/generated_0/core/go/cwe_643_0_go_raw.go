package main

import (
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Parse the XML data securely with XXE prevention
	xmlTree, err := xmltree.ParseXML([]byte(xmlData), xmltree.DisableEntity(true))
	if err != nil {
		return "", "", ""
	}

	// Construct the XPath query with parameterized inputs
	query := goxpath.MustParse(`//student[username[text()=$username] and password[text()=$password]]`)

	// Execute the XPath query with sanitized inputs
	results, err := query.Exec(xmlTree, goxpath.StringVar("username", username), goxpath.StringVar("password", password))
	if err != nil || len(results) == 0 {
		return "", "", ""
	}

	// Extract the student information
	studentNode := results[0]
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