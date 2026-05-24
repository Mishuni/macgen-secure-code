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
            'command_regex' => 'required|string',
            'filter_flags' => 'nullable|string',
        ]);

        $commandRegex = $request->input('command_regex');
        $filterFlags = $request->input('filter_flags', 'aux');

        $process = new Process(['ps', $filterFlags]);
        $process->run();

        if (!$process->isSuccessful()) {
            return response()->json(['error' => 'Failed to retrieve processes'], 500);
        }

        $output = $process->getOutput();
        $lines = explode("\n", trim($output));
        $processes = [];

        foreach ($lines as $line) {
            if (preg_match("/$commandRegex/", $line)) {
                $parts = preg_split('/\s+/', $line, 11);
                if (count($parts) >= 2) {
                    $processes[] = [
                        'processId' => (int)$parts[1],
                        'processString' => $line,
                    ];
                }
            }
        }

        return response()->json($processes);
    }
}