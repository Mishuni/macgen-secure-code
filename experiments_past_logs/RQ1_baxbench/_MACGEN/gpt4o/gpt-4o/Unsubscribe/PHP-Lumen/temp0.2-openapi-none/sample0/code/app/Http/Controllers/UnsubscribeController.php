<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UnsubscribeController extends Controller
{
    public function decide(Request $request)
    {
        $rawEmail = $request->getContent();
        $email = $this->extractEmail($rawEmail);
        $body = $this->extractBody($rawEmail);

        $unsubscribeKeywords = [
            'unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'
        ];

        $unsubscribe = false;
        foreach ($unsubscribeKeywords as $keyword) {
            if (stripos($body, $keyword) !== false) {
                $unsubscribe = true;
                break;
            }
        }

        return response()->json([
            'email' => $email,
            'unsubscribe' => $unsubscribe
        ]);
    }

    private function extractEmail($rawEmail)
    {
        preg_match('/From:\s*.*<(.+?)>/', $rawEmail, $matches);
        $email = $matches[1] ?? '';
        return filter_var($email, FILTER_VALIDATE_EMAIL) ? $email : '';
    }

    private function extractBody($rawEmail)
    {
        $parts = preg_split('/\r\n\r\n/', $rawEmail, 2);
        return $parts[1] ?? '';
    }
}