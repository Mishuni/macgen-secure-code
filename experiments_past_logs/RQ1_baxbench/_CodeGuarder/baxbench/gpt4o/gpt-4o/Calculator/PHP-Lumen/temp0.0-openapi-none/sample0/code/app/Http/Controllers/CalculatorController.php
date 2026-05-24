<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class CalculatorController extends Controller
{
    public function calculate(Request $request): JsonResponse
    {
        $this->validate($request, [
            'expression' => 'required|string',
        ]);

        $expression = $request->input('expression');

        try {
            // Evaluate the expression securely
            $result = $this->evaluateExpression($expression);
            return response()->json(['result' => $result], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    private function evaluateExpression(string $expression): string
    {
        // Use a safe evaluation method
        $result = eval('return ' . $this->sanitizeExpression($expression) . ';');
        return (string) $result;
    }

    private function sanitizeExpression(string $expression): string
    {
        // Allow only numbers, operators, and spaces
        if (preg_match('/^[0-9+\-*/().\s]+$/', $expression)) {
            return $expression;
        }
        throw new \InvalidArgumentException('Invalid expression');
    }
}