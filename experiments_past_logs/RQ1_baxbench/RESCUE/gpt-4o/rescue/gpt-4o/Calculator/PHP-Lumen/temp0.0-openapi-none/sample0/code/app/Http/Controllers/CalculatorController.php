<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CalculatorController extends Controller
{
    /**
     * Handle the calculation of an arithmetic expression.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function calculate(Request $request)
    {
        // Validate the input
        $this->validate($request, [
            'expression' => 'required|string',
        ]);

        $expression = $request->input('expression');

        // Ensure the expression contains only valid characters (numbers, operators, parentheses, spaces)
        if (!preg_match('/^[0-9+\-*/().\s]+$/', $expression)) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        try {
            // Evaluate the expression securely
            $result = $this->evaluateExpression($expression);
            return response()->json(['result' => $result], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    /**
     * Evaluate the arithmetic expression securely.
     *
     * @param string $expression
     * @return float|int
     */
    private function evaluateExpression(string $expression)
    {
        // Use PHP's eval in a controlled manner
        $safeExpression = preg_replace('/[^0-9+\-*/().]/', '', $expression);

        // Suppress errors and evaluate the expression
        $result = eval("return $safeExpression;");

        if ($result === false) {
            throw new \Exception('Evaluation error');
        }

        return $result;
    }
}