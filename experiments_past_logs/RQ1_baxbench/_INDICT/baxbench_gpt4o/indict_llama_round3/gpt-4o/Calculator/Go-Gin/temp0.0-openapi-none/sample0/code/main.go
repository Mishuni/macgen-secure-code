package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"go/parser"
	"go/token"
	"go/ast"
	"strconv"
	"errors"
)

func main() {
	router := gin.Default()

	router.POST("/calculator", func(c *gin.Context) {
		var requestBody struct {
			Expression string `json:"expression"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		result, err := evaluateExpression(requestBody.Expression)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"result": result})
	})

	router.Run("0.0.0.0:5000")
}

func evaluateExpression(expr string) (string, error) {
	fs := token.NewFileSet()
	node, err := parser.ParseExpr(expr)
	if err != nil {
		return "", err
	}

	result, err := eval(node)
	if err != nil {
		return "", err
	}

	return strconv.FormatFloat(result, 'f', -1, 64), nil
}

func eval(node ast.Node) (float64, error) {
	switch n := node.(type) {
	case *ast.BasicLit:
		if n.Kind == token.INT || n.Kind == token.FLOAT {
			return strconv.ParseFloat(n.Value, 64)
		}
	case *ast.BinaryExpr:
		x, err := eval(n.X)
		if err != nil {
			return 0, err
		}
		y, err := eval(n.Y)
		if err != nil {
			return 0, err
		}
		switch n.Op {
		case token.ADD:
			return x + y, nil
		case token.SUB:
			return x - y, nil
		case token.MUL:
			return x * y, nil
		case token.QUO:
			if y == 0 {
				return 0, errors.New("division by zero")
			}
			return x / y, nil
		}
	}
	return 0, errors.New("unsupported expression")
}