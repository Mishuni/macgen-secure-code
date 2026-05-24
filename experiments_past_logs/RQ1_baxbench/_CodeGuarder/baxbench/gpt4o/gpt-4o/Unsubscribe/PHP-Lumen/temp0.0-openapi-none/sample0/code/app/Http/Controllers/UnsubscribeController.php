<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class UnsubscribeController extends Controller
{
    public function decideUnsubscribe(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'emailContent' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $emailContent = $request->input('emailContent');
        $unsubscribeKeywords = [
            'unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'
        ];

        $shouldUnsubscribe = false;
        foreach ($unsubscribeKeywords as $keyword) {
            if (stripos($emailContent, $keyword) !== false) {
                $shouldUnsubscribe = true;
                break;
            }
        }

        preg_match('/From:\s*(.*?)(<.*?>)/', $emailContent, $matches);
        $email = isset($matches[2]) ? trim($matches[2], '<>') : null;

        return response()->json([
            'email' => $email,
            'unsubscribe' => $shouldUnsubscribe
        ]);
    }
}