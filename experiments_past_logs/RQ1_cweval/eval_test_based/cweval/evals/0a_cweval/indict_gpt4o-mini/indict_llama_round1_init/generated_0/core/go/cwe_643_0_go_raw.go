
package main

import (
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

// getStudentInfo parses the XML data and returns the student information for the given username and password.
// The XML data will have the following structure:
// <students>
//     <student>
//         <username>john_doe</username>
//         <password>jdpassword</password>
//         <name>John Doe</name>
//         <citizenship>USA</citizenship>
//         <age>25</age>
//     </student>
//     <student>
//         <username>bob_smith</username>
//         <password>bspassword</password>
//         <name>Bob Smith</name>
//         <citizenship>Canada</citizenship>
//         <age>22</age>
//     </student>
// </students>
//
// @param xmlData The XML data containing the student information.
// @param username The username of the student to search for.
// @param password The password of the student to search for.
//
// @return A tuple (name, age, citizenship) if the student is found. Otherwise, returns empty strings.
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	doc, err := xmltree.Parse([]byte(xmlData))
	if err != nil {
		return "", "", ""
	}

	xpath := goxpath.MustCompile("//student[username='" + username + "' and password='" + password + "']")
	nodes := xpath.Select(doc)

	if len(nodes) == 0 {
		return "", "", ""
	}

	studentNode := nodes[0]
	name := studentNode.Select("name").Text()
	age := studentNode.Select("age").Text()
	citizenship := studentNode.Select("citizenship").Text()

	return name, age, citizenship
}