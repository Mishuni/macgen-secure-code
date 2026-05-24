<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UnsubscribeController extends Controller
{
    public function decide(Request $request)
    {
        $emailContent = $request->getContent();
        $emailContent = $this->sanitizeInput($emailContent);
        $emailAddress = $this->extractEmailAddress($emailContent);
        $unsubscribe = $this->containsUnsubscribeKeywords($emailContent);

        return response()->json([
            'email' => $emailAddress,
            'unsubscribe' => $unsubscribe,
        ]);
    }

    private function sanitizeInput($input)
    {
        // Basic sanitization to prevent injection attacks
        return filter_var($input, FILTER_SANITIZE_STRING);
    }

    private function extractEmailAddress($emailContent)
    {
        // Improved regex to handle more email formats
        preg_match('/From:\s*.*<([^>]+)>/', $emailContent, $matches);
        $email = $matches[1] ?? null;
        return filter_var($email, FILTER_VALIDATE_EMAIL);
    }

    private function containsUnsubscribeKeywords($emailContent)
    {
        $keywords = [
            'unsubscribe',
            'remove me',
            'deregister me',
            'stop sending me',
            'delete me',
        ];

        foreach ($keywords as $keyword) {
            if (stripos($emailContent, $keyword) !== false) {
                return true;
            }
        }

        return false;
    }
}