<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class ProcessController extends Controller
{
    public function monitorProcesses(Request $request)
    {
        $request->validate([
            'filter_flags' => 'string|nullable',
            'command_regex' => 'required|string',
        ]);

        $commandRegex = $request->input('command_regex');
        $filterFlags = $request->input('filter_flags', 'aux');

        // Validate the command regex to prevent command injection
        if (!preg_match('/^[\w\s\.\*\-]+$/', $commandRegex)) {
            return response()->json(['code' => 400, 'message' => 'Invalid command regex format.'], 400);
        }

        // Execute the command safely
        $command = "ps $filterFlags | grep -E '$commandRegex'";
        exec($command, $output, $returnVar);

        if ($returnVar !== 0) {
            Log::error('Command execution failed', ['command' => $command, 'output' => $output]);
            return response()->json(['code' => 500, 'message' => 'Failed to retrieve processes.'], 500);
        }

        $processes = [];
        foreach ($output as $line) {
            if (preg_match('/^\s*(\d+)\s+(.+)$/', $line, $matches)) {
                $processes[] = [
                    'processId' => (int)$matches[1],
                    'processString' => trim($matches[2]),
                ];
            }
        }

        return response()->json($processes);
    }
}