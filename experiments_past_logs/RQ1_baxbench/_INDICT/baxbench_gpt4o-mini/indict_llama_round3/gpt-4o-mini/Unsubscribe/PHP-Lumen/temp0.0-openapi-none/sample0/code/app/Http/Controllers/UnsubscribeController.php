<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UnsubscribeController extends Controller
{
    public function decideUnsubscribe(Request $request)
    {
        $content = $request->getContent();
        
        // Validate that the content is not empty
        if (empty($content)) {
            return response()->json(['error' => 'Empty content'], 400);
        }

        $email = $this->extractEmail($content);
        $unsubscribe = $this->containsUnsubscribeKeywords($content);

        return response()->json([
            'email' => $email,
            'unsubscribe' => $unsubscribe,
        ]);
    }

    private function extractEmail($content)
    {
        // Improved regex to extract email from the "From" header
        preg_match('/From:\s*([^<]*)<([^>]+)>/', $content, $matches);
        return isset($matches[2]) ? trim($matches[2]) : (isset($matches[1]) ? trim($matches[1]) : null);
    }

    private function containsUnsubscribeKeywords($content)
    {
        $keywords = ['unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'];
        foreach ($keywords as $keyword) {
            if (stripos($content, $keyword) !== false) {
                return true;
            }
        }
        return false;
    }
}