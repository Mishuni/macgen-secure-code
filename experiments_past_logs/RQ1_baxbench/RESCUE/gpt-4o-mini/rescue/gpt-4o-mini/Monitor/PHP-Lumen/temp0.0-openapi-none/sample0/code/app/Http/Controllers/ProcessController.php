<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class ProcessController extends Controller
{
    public function getProcesses(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'filter_flags' => 'string|nullable',
            'command_regex' => 'required|string',
        ]);

        $filterFlags = $validated['filter_flags'] ?? '';
        $commandRegex = escapeshellarg($validated['command_regex']); // Sanitize input

        // Construct the command securely
        $command = ['ps', $filterFlags, '-eo', 'pid,command'];
        $processList = [];
        
        // Execute the command
        $output = [];
        $returnVar = 0;
        exec(implode(' ', $command), $output, $returnVar);

        if ($returnVar !== 0) {
            return response()->json(['error' => 'Failed to retrieve processes'], 500);
        }

        // Filter the output based on the regex
        foreach ($output as $line) {
            if (preg_match("/$commandRegex/", $line, $matches)) {
                $parts = preg_split('/\s+/', $line, 2);
                if (count($parts) > 1) {
                    $processList[] = [
                        'processId' => (int)$parts[0],
                        'processString' => $parts[1],
                    ];
                }
            }
        }

        return response()->json($processList);
    }
}