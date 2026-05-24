<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class LoggingController extends Controller
{
    private $logFilePath = __DIR__ . '/../../../storage/logs/logs.txt';

    public function logMessage(Request $request)
    {
        $this->validate($request, [
            'message' => 'required|string',
        ]);

        $message = $request->input('message');
        file_put_contents($this->logFilePath, $message . PHP_EOL, FILE_APPEND | LOCK_EX);

        return response()->json(['status' => 'Log message successful'], 200);
    }

    public function getLogs()
    {
        if (!file_exists($this->logFilePath)) {
            return response()->json(['logs' => ''], 200);
        }

        $logs = file_get_contents($this->logFilePath);
        return response($logs, 200)->header('Content-Type', 'text/plain');
    }
}