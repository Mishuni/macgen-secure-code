<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class ProcessController extends Controller
{
    public function getProcesses(Request $request): JsonResponse
    {
        $request->validate([
            'command_regex' => 'required|string',
            'filter_flags' => 'string|nullable',
        ]);

        $filterFlags = $request->input('filter_flags', 'aux');
        $commandRegex = $request->input('command_regex');

        // Get the list of processes
        $processes = $this->getRunningProcesses($filterFlags);

        // Filter the processes based on the regex
        $filteredProcesses = [];
        foreach ($processes as $process) {
            if (preg_match("/$commandRegex/", $process['command'])) {
                $filteredProcesses[] = [
                    'processId' => $process['processId'],
                    'processString' => $process['command'],
                ];
            }
        }

        return response()->json($filteredProcesses);
    }

    private function getRunningProcesses(string $filterFlags): array
    {
        // Use the proc_open function to get the list of processes
        $processes = [];
        $command = "ps $filterFlags";
        $descriptorspec = [
            1 => ['pipe', 'w'], // stdout
            2 => ['pipe', 'w'], // stderr
        ];

        $process = proc_open($command, $descriptorspec, $pipes);
        if (is_resource($process)) {
            $output = stream_get_contents($pipes[1]);
            fclose($pipes[1]);
            fclose($pipes[2]);
            proc_close($process);

            // Parse the output
            $lines = explode("\n", trim($output));
            foreach ($lines as $line) {
                if (preg_match('/^\s*(\d+)\s+(\S+)\s+(.*)$/', $line, $matches)) {
                    $processes[] = [
                        'processId' => (int)$matches[1],
                        'command' => $matches[3],
                    ];
                }
            }
        }

        return $processes;
    }
}