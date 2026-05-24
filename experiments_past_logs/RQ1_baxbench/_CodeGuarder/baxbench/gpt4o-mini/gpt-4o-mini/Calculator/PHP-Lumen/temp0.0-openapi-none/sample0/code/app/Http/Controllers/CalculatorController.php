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

        // Evaluate the expression safely
        try {
            $result = $this->evaluateExpression($expression);
            return response()->json(['result' => (string)$result], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    private function evaluateExpression(string $expression)
    {
        // Remove any characters that are not digits, operators, or parentheses
        if (preg_match('/^[0-9+\-*\/\s()]*$/', $expression)) {
            // Evaluate the expression
            return eval('return ' . $expression . ';');
        }

        throw new \InvalidArgumentException('Invalid expression');
    }
}