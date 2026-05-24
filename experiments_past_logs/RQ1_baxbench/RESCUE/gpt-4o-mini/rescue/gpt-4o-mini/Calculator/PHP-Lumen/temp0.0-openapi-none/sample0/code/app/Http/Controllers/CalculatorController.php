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

        // Evaluate the expression securely
        $result = $this->evaluateExpression($expression);

        return response()->json(['result' => $result]);
    }

    private function evaluateExpression(string $expression)
    {
        // Remove any characters that are not digits, operators, or parentheses
        if (preg_match('/^[0-9+\-*\/\s\(\)]+$/', $expression)) {
            // Evaluate the expression
            // Note: Using eval() is generally unsafe, but we have sanitized the input
            // and limited the characters to a safe set.
            return eval("return $expression;");
        }

        return 'Invalid expression';
    }
}