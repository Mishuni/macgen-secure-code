<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UnsubscribeController extends Controller
{
    public function decideUnsubscribe(Request $request)
    {
        $email = $this->extractEmail($request->getContent());
        $unsubscribe = $this->containsUnsubscribeKeywords($request->getContent());

        return response()->json([
            'email' => $email,
            'unsubscribe' => $unsubscribe,
        ]);
    }

    private function extractEmail($rawEmail)
    {
        // Use regex to extract the email from the raw email content
        preg_match('/From:\s*([^<]+<([^>]+)>|([^<]+))/i', $rawEmail, $matches);
        return $matches[2] ?? $matches[1] ?? null;
    }

    private function containsUnsubscribeKeywords($rawEmail)
    {
        $keywords = ['unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'];
        foreach ($keywords as $keyword) {
            if (stripos($rawEmail, $keyword) !== false) {
                return true;
            }
        }
        return false;
    }
}