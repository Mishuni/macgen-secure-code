<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class MonitorController extends Controller
{
    public function getProcesses(Request $request)
    {
        $this->validate($request, [
            'filter_flags' => 'string|nullable',
            'command_regex' => 'required|string',
        ]);

        $filterFlags = $request->input('filter_flags', 'aux');
        $commandRegex = $request->input('command_regex');

        // Validate filter flags to prevent command injection
        if (!preg_match('/^[a-zA-Z\s\-]*$/', $filterFlags)) {
            return response()->json(['error' => 'Invalid filter flags'], 400);
        }

        // Validate regex to prevent potential DoS
        if (@preg_match("/$commandRegex/", null) === false) {
            return response()->json(['error' => 'Invalid regular expression'], 400);
        }

        $process = new Process(['ps', $filterFlags]);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        $output = $process->getOutput();
        $lines = explode("\n", trim($output));
        $matchingProcesses = [];

        foreach ($lines as $line) {
            if (preg_match("/$commandRegex/", $line)) {
                $columns = preg_split('/\s+/', $line, 11);
                if (count($columns) >= 2) {
                    $matchingProcesses[] = [
                        'processId' => (int)$columns[1],
                        'processString' => $line,
                    ];
                }
            }
        }

        return response()->json($matchingProcesses);
    }
}