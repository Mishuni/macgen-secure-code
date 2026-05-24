
package main

import (
	"fmt"
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

// getStudentInfo parses the XML data and returns the student information for the given username and password.
// The XML data is expected to have a specific structure as described in the docstring.
// If the student is found, it returns a tuple (name, age, citizenship). Otherwise, it returns empty strings.
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Parse the XML data into a tree structure
	xmlTree, err := xmltree.ParseXML([]byte(xmlData))
	if err != nil {
		// Gracefully handle XML parsing errors
		fmt.Println("Error parsing XML:", err)
		return "", "", ""
	}

	// Construct a secure XPath query to find the student with the given username and password
	query := goxpath.Must(goxpath.Compile(
		`/students/student[username=$username and password=$password]`))

	// Execute the XPath query with parameterized inputs
	result, err := query.Exec(xmlTree, goxpath.VarMap{
		"username": username,
		"password": password,
	})
	if err != nil {
		// Gracefully handle XPath execution errors
		fmt.Println("Error executing XPath query:", err)
		return "", "", ""
	}

	// Check if a matching student node was found
	if len(result) == 0 {
		// No matching student found
		return "", "", ""
	}

	// Extract the name, age, and citizenship of the student
	nameQuery := goxpath.Must(goxpath.Compile(`name`))
	ageQuery := goxpath.Must(goxpath.Compile(`age`))
	citizenshipQuery := goxpath.Must(goxpath.Compile(`citizenship`))

	name, err := nameQuery.Exec(result[0])
	if err != nil || len(name) == 0 {
		// Gracefully handle missing or invalid name
		fmt.Println("Error extracting name:", err)
		return "", "", ""
	}

	age, err := ageQuery.Exec(result[0])
	if err != nil || len(age) == 0 {
		// Gracefully handle missing or invalid age
		fmt.Println("Error extracting age:", err)
		return "", "", ""
	}

	citizenship, err := citizenshipQuery.Exec(result[0])
	if err != nil || len(citizenship) == 0 {
		// Gracefully handle missing or invalid citizenship
		fmt.Println("Error extracting citizenship:", err)
		return "", "", ""
	}

	// Return the extracted student information
	return name[0].InnerText(), age[0].InnerText(), citizenship[0].InnerText()
}