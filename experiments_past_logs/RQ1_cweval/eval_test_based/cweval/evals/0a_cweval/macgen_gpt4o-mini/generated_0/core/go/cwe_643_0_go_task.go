package main

import (
	"fmt"
	"os"
	"regexp"

	"github.com/ChrisTrenkamp/goxpath"
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
