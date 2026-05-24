<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class UnsubscribeController extends Controller
{
    public function decideUnsubscribe(Request $request): JsonResponse
    {
        $email = $this->extractEmail($request->getContent());
        $unsubscribe = $this->containsUnsubscribeRequest($request->getContent());

        return response()->json([
            'email' => $email,
            'unsubscribe' => $unsubscribe,
        ]);
    }

    private function extractEmail(string $emailContent): ?string
    {
        preg_match('/From:\s*(.*?)(?:\r\n|\n)/', $emailContent, $matches);
        return $matches[1] ?? null;
    }

    private function containsUnsubscribeRequest(string $emailContent): bool
    {
        $unsubscribeKeywords = [
            'unsubscribe',
            'remove me',
            'deregister me',
            'stop sending me',
            'delete me',
        ];

        foreach ($unsubscribeKeywords as $keyword) {
            if (stripos($emailContent, $keyword) !== false) {
                return true;
            }
        }

        return false;
    }
}