<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UnsubscribeController extends Controller
{
    /**
     * Handle the unsubscribe decision.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function decide(Request $request)
    {
        // Validate the request body
        $this->validate($request, [
            '' => 'required|string',
        ]);

        $rawEmail = $request->getContent();

        // Extract the "From" email address
        $email = $this->extractEmail($rawEmail);

        // Check if the email contains unsubscribe keywords
        $unsubscribeKeywords = [
            'unsubscribe',
            'remove me',
            'deregister me',
            'stop sending me',
            'delete me',
        ];

        $unsubscribe = false;
        foreach ($unsubscribeKeywords as $keyword) {
            if (stripos($rawEmail, $keyword) !== false) {
                $unsubscribe = true;
                break;
            }
        }

        return response()->json([
            'email' => $email,
            'unsubscribe' => $unsubscribe,
        ]);
    }

    /**
     * Extract the email address from the raw email content.
     *
     * @param string $rawEmail
     * @return string|null
     */
    private function extractEmail(string $rawEmail): ?string
    {
        // Match the "From" header using a regular expression
        if (preg_match('/^From:\s*.*<(.+?)>/mi', $rawEmail, $matches)) {
            return $matches[1];
        }

        return null;
    }
}