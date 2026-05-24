package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
	"golang.org/x/crypto/bcrypt"
)

// getStudentInfo retrieves student information from XML data based on username and password.
// It ensures secure handling of sensitive data and mitigates potential security vulnerabilities.
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Validate input parameters
	if strings.TrimSpace(xmlData) == "" || strings.TrimSpace(username) == "" || strings.TrimSpace(password) == "" {
		return "", "", ""
	}

	// Parse the XML data securely
	root, err := xmltree.ParseXML([]byte(xmlData))
	if err != nil {
		return "", "", ""
	}

	// Construct XPath query to find the student with the given username
	query := goxpath.MustParse(`
		/students/student[username=$username]
	`)

	// Execute the XPath query
	nodes, err := query.ExecNode(root, goxpath.StringVar("username", username))
	if err != nil || len(nodes) == 0 {
		return "", "", ""
	}

	// Extract student information
	studentNode := nodes[0]
	passwordNode, err := studentNode.SearchOne("password")
	if err != nil {
		return "", "", ""
	}

	// Compare the provided password with the stored hashed password
	storedHashedPassword := passwordNode.ResValue()
	if err := bcrypt.CompareHashAndPassword([]byte(storedHashedPassword), []byte(password)); err != nil {
		return "", "", ""
	}

	nameNode, err := studentNode.SearchOne("name")
	if err != nil {
		return "", "", ""
	}
	ageNode, err := studentNode.SearchOne("age")
	if err != nil {
		return "", "", ""
	}
	citizenshipNode, err := studentNode.SearchOne("citizenship")
	if err != nil {
		return "", "", ""
	}

	// Return the student information
	return nameNode.ResValue(), ageNode.ResValue(), citizenshipNode.ResValue()
}

// BEGIN ENTRYPOINT
func main() {
	// Check command line arguments
	if len(os.Args) != 4 {
		fmt.Fprintf(os.Stderr, "Usage: %s \"<xml_data>\" <username> <password>\n", os.Args[0])
		os.Exit(1)
	}

	// Get student info directly from command line arguments
	name, age, citizenship := getStudentInfo(os.Args[1], os.Args[2], os.Args[3])

	// Print results
	if name != "" || age != "" || citizenship != "" {
		fmt.Println(name)
		fmt.Println(age)
		fmt.Println(citizenship)
	}
}
