<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UnsubscribeController extends Controller
{
    public function decideUnsubscribe(Request $request)
    {
        $rawEmail = $request->getContent();
        
        // Extract email from raw email content
        preg_match('/From:\s*(.*?)(\r\n|\n)/', $rawEmail, $matches);
        $email = isset($matches[1]) ? trim($matches[1]) : null;

        // Validate email format
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return response()->json(['error' => 'Invalid email format'], 400);
        }

        // Check for unsubscribe keywords
        $unsubscribeKeywords = ['unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'];
        $body = $this->extractBody($rawEmail);
        $unsubscribe = $this->containsUnsubscribeKeywords($body, $unsubscribeKeywords);

        return response()->json(['email' => $email, 'unsubscribe' => $unsubscribe]);
    }

    private function extractBody($rawEmail)
    {
        // Logic to extract the body from the raw email content
        preg_match('/Content-Type:text\/plain; charset="UTF-8"\s*Content-Transfer-Encoding:quoted-printable\s*(.*?)(--)/s', $rawEmail, $matches);
        return trim($matches[1] ?? '');
    }

    private function containsUnsubscribeKeywords($body, $keywords)
    {
        foreach ($keywords as $keyword) {
            if (stripos($body, $keyword) !== false) {
                return true;
            }
        }
        return false;
    }
}