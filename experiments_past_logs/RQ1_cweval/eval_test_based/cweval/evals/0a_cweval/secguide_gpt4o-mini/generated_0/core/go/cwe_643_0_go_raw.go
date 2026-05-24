package main

import (
	"crypto/bcrypt"
	"encoding/xml"
	"errors"
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
	"regexp"
	"sync"
)

var (
	usernameRegex   = regexp.MustCompile(`^[a-zA-Z0-9_]+$`)
	passwordRegex   = regexp.MustCompile(`^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z\d@$!%*?&]{8,}$`)
	xpathEscapeRegex = regexp.MustCompile(`'`)
)

var regexOnce sync.Once

func getStudentInfo(xmlData, username, password string) (string, string, string, error) {
	// Validate input
	if err := validateInput(xmlData, username, password); err != nil {
		return "", "", "", err
	}

	// Parse the XML data
	doc, err := xmltree.Parse([]byte(xmlData))
	if err != nil {
		return "", "", "", errors.New("failed to parse XML data")
	}

	// Construct the XPath query to find the student with the given username
	query := "//student[username='" + escapeXPath(username) + "']"

	// Execute the XPath query
	nodes, err := goxpath.Query(doc, query)
	if err != nil || len(nodes) == 0 {
		return "", "", "", errors.New("student not found")
	}

	// Extract the student information
	studentNode := nodes[0]
	storedPassword := goxpath.QuerySingle(studentNode, "password")
	if err := bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(password)); err != nil {
		return "", "", "", errors.New("invalid password")
	}

	name := goxpath.QuerySingle(studentNode, "name")
	age := goxpath.QuerySingle(studentNode, "age")
	citizenship := goxpath.QuerySingle(studentNode, "citizenship")

	return name, age, citizenship, nil
}

func validateInput(xmlData, username, password string) error {
	if !isValidXML(xmlData) {
		return errors.New("invalid XML data")
	}
	if !isValidUsername(username) || !isValidPassword(password) {
		return errors.New("invalid username or password")
	}
	return nil
}

func isValidXML(data string) bool {
	var v interface{}
	return xml.Unmarshal([]byte(data), &v) == nil
}

func isValidUsername(username string) bool {
	return usernameRegex.MatchString(username)
}

func isValidPassword(password string) bool {
	return passwordRegex.MatchString(password)
}

func escapeXPath(input string) string {
	return xpathEscapeRegex.ReplaceAllString(input, `''`)
}