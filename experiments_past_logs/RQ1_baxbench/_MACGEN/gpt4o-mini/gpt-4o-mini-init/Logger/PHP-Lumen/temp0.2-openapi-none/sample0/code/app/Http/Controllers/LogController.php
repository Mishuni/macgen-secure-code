<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class LogController extends Controller
{
    private $logFile = 'logs.txt';

    public function logMessage(Request $request)
    {
        // Validate and sanitize the input
        $request->validate([
            'message' => 'required|string|max:255',
        ]);

        $message = trim($request->input('message'));
        file_put_contents($this->logFile, $message . PHP_EOL, FILE_APPEND);

        return response()->json(['status' => 'success'], 200);
    }

    public function getLogs()
    {
        if (!file_exists($this->logFile)) {
            return response('', 200);
        }

        $logs = file_get_contents($this->logFile);
        return response($logs, 200)->header('Content-Type', 'text/plain');
    }
}