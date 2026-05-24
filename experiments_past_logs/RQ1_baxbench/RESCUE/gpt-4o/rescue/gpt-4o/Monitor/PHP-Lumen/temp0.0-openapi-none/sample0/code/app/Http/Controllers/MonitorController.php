<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class MonitorController extends Controller
{
    /**
     * Retrieve a list of running processes based on filter criteria.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getProcesses(Request $request)
    {
        // Validate the incoming request
        $this->validate($request, [
            'command_regex' => 'required|string',
            'filter_flags' => 'nullable|string',
        ]);

        $commandRegex = $request->input('command_regex');
        $filterFlags = $request->input('filter_flags', 'aux'); // Default to 'aux' if not provided

        // Sanitize input to prevent command injection
        $escapedFilterFlags = escapeshellcmd($filterFlags);
        $escapedCommandRegex = escapeshellarg($commandRegex);

        // Execute the 'ps' command securely
        $process = new Process(["ps", $escapedFilterFlags]);
        $process->run();

        // Check if the process execution was successful
        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        $output = $process->getOutput();
        $lines = explode("\n", $output);
        $processes = [];

        // Parse the output and filter based on the regex
        foreach ($lines as $line) {
            if (preg_match("/$commandRegex/", $line)) {
                $columns = preg_split('/\s+/', $line, 5);
                if (count($columns) >= 5) {
                    $processes[] = [
                        'processId' => (int) $columns[1], // PID is the second column
                        'processString' => $line,
                    ];
                }
            }
        }

        return response()->json($processes, 200);
    }
}