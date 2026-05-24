<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class LogController extends Controller
{
    private $logFilePath;

    public function __construct()
    {
        $this->logFilePath = storage_path('logs/logs.txt');
    }

    public function logMessage(Request $request)
    {
        // Validate the request
        $request->validate([
            'message' => 'required|string|max:255',
        ]);

        // Sanitize the message
        $message = htmlspecialchars($request->input('message'), ENT_QUOTES, 'UTF-8');

        // Log the message to the file
        file_put_contents($this->logFilePath, $message . PHP_EOL, FILE_APPEND);

        return response()->json(['status' => 'success'], 200);
    }

    public function getLogs()
    {
        // Read the log file
        if (file_exists($this->logFilePath)) {
            $logs = file_get_contents($this->logFilePath);
            return response($logs, 200)->header('Content-Type', 'text/plain');
        }

        return response('No logs found', 404);
    }
}