<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class LogController extends Controller
{
    protected $logFile;

    public function __construct()
    {
        $this->logFile = storage_path('logs.txt');
    }

    public function store(Request $request)
    {
        $this->validate($request, [
            'message' => 'required|string',
        ]);

        $message = htmlspecialchars($request->input('message'), ENT_QUOTES, 'UTF-8');
        file_put_contents($this->logFile, $message . PHP_EOL, FILE_APPEND | LOCK_EX);

        return response()->json(['message' => 'Log message successful'], 200);
    }

    public function index()
    {
        $logs = file_exists($this->logFile) ? file_get_contents($this->logFile) : '';

        return response($logs, 200)->header('Content-Type', 'text/plain');
    }
}