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
            $result = $this->evaluateExpression($expression);
            return response()->json(['result' => (string)$result], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    private function evaluateExpression(string $expression)
    {
        // Basic validation to allow only numbers and operators
        if (!preg_match('/^[0-9+\-*/().\s]+$/', $expression)) {
            throw new \InvalidArgumentException('Invalid characters in expression');
        }

        // Evaluate the expression safely
        $result = eval('return ' . $expression . ';');
        if ($result === false) {
            throw new \RuntimeException('Error evaluating expression');
        }

        return $result;
    }
}