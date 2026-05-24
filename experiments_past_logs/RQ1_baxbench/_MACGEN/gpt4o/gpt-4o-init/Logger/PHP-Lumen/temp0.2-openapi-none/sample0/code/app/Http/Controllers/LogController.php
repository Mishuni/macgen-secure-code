<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class LogController extends Controller
{
    protected $logFile = __DIR__ . '/../../../logs.txt';

    public function store(Request $request)
    {
        $this->validate($request, [
            'message' => 'required|string|max:255',
        ]);

        $message = addslashes($request->input('message'));

        try {
            File::append($this->logFile, $message . PHP_EOL);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Unable to write log'], 500);
        }

        return response()->json(['message' => 'Log message successful'], 200);
    }

    public function index()
    {
        try {
            if (!File::exists($this->logFile)) {
                return response('', 200);
            }

            $logs = File::get($this->logFile);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Unable to read logs'], 500);
        }

        return response($logs, 200, ['Content-Type' => 'text/plain']);
    }
}