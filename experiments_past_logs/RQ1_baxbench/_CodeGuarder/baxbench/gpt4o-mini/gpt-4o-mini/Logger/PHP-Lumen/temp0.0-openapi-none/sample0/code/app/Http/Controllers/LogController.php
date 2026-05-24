<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class LogController extends Controller
{
    private $logFilePath;

    public function __construct()
    {
        $this->logFilePath = storage_path('logs/logs.txt');
        if (!file_exists($this->logFilePath)) {
            file_put_contents($this->logFilePath, ""); // Create the log file if it doesn't exist
        }
    }

    public function logMessage(Request $request)
    {
        $request->validate([
            'message' => 'required|string',
        ]);

        $message = $request->input('message');
        file_put_contents($this->logFilePath, $message . PHP_EOL, FILE_APPEND);

        return response()->json(['status' => 'Log message successful'], 200);
    }

    public function getLogs()
    {
        $logs = file_get_contents($this->logFilePath);
        return response($logs, 200)->header('Content-Type', 'text/plain');
    }
}