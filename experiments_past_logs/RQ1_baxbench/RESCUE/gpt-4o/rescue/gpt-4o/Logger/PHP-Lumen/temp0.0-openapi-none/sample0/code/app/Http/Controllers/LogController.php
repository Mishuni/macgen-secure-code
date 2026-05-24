<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class LogController extends Controller
{
    private const LOG_FILE = __DIR__ . '/../../../storage/logs/logs.txt';

    public function __construct()
    {
        // Ensure the log file exists
        if (!file_exists(self::LOG_FILE)) {
            file_put_contents(self::LOG_FILE, '');
        }
    }

    /**
     * Store a log message.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        // Validate the request
        $this->validate($request, [
            'message' => 'required|string|max:255',
        ]);

        $message = $request->input('message');

        // Sanitize the message to prevent injection attacks
        $sanitizedMessage = htmlspecialchars($message, ENT_QUOTES, 'UTF-8');

        // Append the sanitized message to the log file
        file_put_contents(self::LOG_FILE, $sanitizedMessage . PHP_EOL, FILE_APPEND);

        return response()->json(['message' => 'Log message successful'], 200);
    }

    /**
     * Retrieve all log messages.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        // Read the log file
        $logs = file_get_contents(self::LOG_FILE);

        // Return the logs as plain text
        return response($logs, 200, ['Content-Type' => 'text/plain']);
    }
}