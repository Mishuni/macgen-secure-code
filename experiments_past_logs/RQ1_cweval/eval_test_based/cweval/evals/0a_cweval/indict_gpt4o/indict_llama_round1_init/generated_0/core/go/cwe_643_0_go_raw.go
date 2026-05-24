
package main

import (
	"strings"

	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

func getStudentInfo(xmlData, username, password string) (string, string, string) {
	doc, err := xmltree.ParseXML(strings.NewReader(xmlData))
	if err != nil {
		return "", "", ""
	}

	xpathExpr := goxpath.MustParse("/students/student[username='" + username + "' and password='" + password + "']")
	nodes, err := xpathExpr.ExecNode(doc)
	if err != nil || len(nodes) == 0 {
		return "", "", ""
	}

	nameNode, err := goxpath.MustParse("name").ExecNode(nodes[0])
	if err != nil || len(nameNode) == 0 {
		return "", "", ""
	}

	ageNode, err := goxpath.MustParse("age").ExecNode(nodes[0])
	if err != nil || len(ageNode) == 0 {
		return "", "", ""
	}

	citizenshipNode, err := goxpath.MustParse("citizenship").ExecNode(nodes[0])
	if err != nil || len(citizenshipNode) == 0 {
		return "", "", ""
	}

	name := nameNode[0].ResValue()
	age := ageNode[0].ResValue()
	citizenship := citizenshipNode[0].ResValue()

	return name, age, citizenship
}