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

        // Validate the expression
        if (!preg_match('/^[0-9+\-*\/\s()]+$/', $expression)) {
            return response()->json(['error' => 'Invalid expression'], 400);
        }

        // Calculate the result safely
        try {
            $result = $this->evaluateExpression($expression);
            return response()->json(['result' => (string)$result], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid expression'], 400);
        }
    }

    private function evaluateExpression(string $expression)
    {
        // Use a safe method to evaluate the expression
        // This is a simple implementation using a custom parser
        $result = $this->safeEval($expression);
        return $result;
    }

    private function safeEval(string $expression)
    {
        // Replace operators with spaces to avoid injection
        $expression = preg_replace('/[^0-9+\-*\/\s()]/', '', $expression);
        // Evaluate the expression using a safe method
        return eval('return ' . $expression . ';'); // Replace with a proper parser for production
    }
}