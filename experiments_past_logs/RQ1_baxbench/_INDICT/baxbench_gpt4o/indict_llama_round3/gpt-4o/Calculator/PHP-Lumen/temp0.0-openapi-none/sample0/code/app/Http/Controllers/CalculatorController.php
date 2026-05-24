<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CalculatorController extends Controller
{
    public function calculate(Request $request)
    {
        $this->validate($request, [
            'expression' => 'required|string',
        ]);

        $expression = $request->input('expression');

        try {
            // Evaluate the expression safely
            $result = $this->evaluateExpression($expression);
            return response()->json(['result' => $result]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    private function evaluateExpression($expression)
    {
        // Tokenize the expression
        $tokens = preg_split('/\s*([\+\-\*\/\(\)])\s*/', $expression, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);

        // Use a stack-based approach to evaluate the expression
        $output = [];
        $operators = [];

        $precedence = ['+' => 1, '-' => 1, '*' => 2, '/' => 2];
        $associativity = ['+' => 'L', '-' => 'L', '*' => 'L', '/' => 'L'];

        foreach ($tokens as $token) {
            if (is_numeric($token)) {
                $output[] = $token;
            } elseif (isset($precedence[$token])) {
                while (!empty($operators) && isset($precedence[end($operators)]) &&
                    (($associativity[$token] == 'L' && $precedence[$token] <= $precedence[end($operators)]) ||
                    ($associativity[$token] == 'R' && $precedence[$token] < $precedence[end($operators)]))) {
                    $output[] = array_pop($operators);
                }
                $operators[] = $token;
            } elseif ($token == '(') {
                $operators[] = $token;
            } elseif ($token == ')') {
                while (!empty($operators) && end($operators) != '(') {
                    $output[] = array_pop($operators);
                }
                array_pop($operators);
            }
        }

        while (!empty($operators)) {
            $output[] = array_pop($operators);
        }

        // Evaluate the RPN expression
        $stack = [];
        foreach ($output as $token) {
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