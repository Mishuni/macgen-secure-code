<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class LogController extends Controller
{
    private $logFilePath;

    public function __construct()
    {
        $this->logFilePath = storage_path('logs.txt');
    }

    public function logMessage(Request $request)
    {
        $request->validate([
            'message' => 'required|string',
        ]);

        $message = $request->input('message');
        // Sanitize the log message to prevent log injection
        $sanitizedMessage = htmlspecialchars($message, ENT_QUOTES, 'UTF-8');
        file_put_contents($this->logFilePath, $sanitizedMessage . PHP_EOL, FILE_APPEND);

        return response()->json(['status' => 'success'], 200);
    }

    public function getLogs()
    {
        if (!file_exists($this->logFilePath)) {
            return response('No logs found.', 200);
        }

        $logs = file_get_contents($this->logFilePath);
        return response($logs, 200)->header('Content-Type', 'text/plain');
    }
}