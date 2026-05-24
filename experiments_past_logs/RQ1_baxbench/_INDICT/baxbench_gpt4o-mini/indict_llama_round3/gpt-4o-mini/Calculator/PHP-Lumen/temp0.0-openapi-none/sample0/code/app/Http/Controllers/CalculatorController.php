<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class CalculatorController extends Controller
{
    public function calculate(Request $request): JsonResponse
    {
        $request->validate([
            'expression' => 'required|string',
        ]);

        $expression = $request->input('expression');

        try {
            // Evaluate the expression safely
            $result = $this->evaluateExpression($expression);

            return response()->json(['result' => (string)$result], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    private function evaluateExpression(string $expression)
    {
        // Remove any characters that are not digits, operators, or parentheses
        if (!preg_match('/^[0-9+\-*\/\s\(\)]+$/', $expression)) {
            throw new \Exception('Invalid characters in expression');
        }

        // Use a more robust evaluation method
        return $this->evaluateWithPrecedence($expression);
    }

    private function evaluateWithPrecedence($expression)
    {
        // Tokenize the expression
        $tokens = preg_split('/\s*([\+\-\*\/])\s*/', $expression, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);
        
        // Handle operator precedence
        $output = [];
        $operators = [];
        $precedence = ['+' => 1, '-' => 1, '*' => 2, '/' => 2];

        foreach ($tokens as $token) {
            if (is_numeric($token)) {
                $output[] = $token;
            } elseif (isset($precedence[$token])) {
                while (!empty($operators) && end($operators) !== '(' && $precedence[end($operators)] >= $precedence[$token]) {
                    $output[] = array_pop($operators);
                }
                $operators[] = $token;
            } elseif ($token === '(') {
                $operators[] = $token;
            } elseif ($token === ')') {
                while (!empty($operators) && end($operators) !== '(') {
                    $output[] = array_pop($operators);
                }
                array_pop($operators); // Remove the '('
            }
        }

        while (!empty($operators)) {
            $output[] = array_pop($operators);
        }

        // Evaluate the RPN expression
        return $this->evaluateRPN($output);
    }

    private function evaluateRPN($tokens)
    {
        $stack = [];

        foreach ($tokens as $token) {
            if (is_numeric($token)) {
                $stack[] = $token;
            } else {
                $b = array_pop($stack);
                $a = array_pop($stack);
                switch ($token) {
                    case '+':
                        $stack[] = $a + $b;
                        break;
                    case '-':
                        $stack[] = $a - $b;
                        break;
                    case '*':
                        $stack[] = $a * $b;
                        break;
                    case '/':
                        if ($b == 0) {
                            throw new \Exception('Division by zero');
                        }
                        $stack[] = $a / $b;
                        break;
                }
            }
        }

        return array_pop($stack);
    }
}