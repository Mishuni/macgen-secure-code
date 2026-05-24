<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class ProcessController extends Controller
{
    public function monitorCommands(Request $request)
    {
        $request->validate([
            'filter_flags' => 'string|max:10|nullable',
            'command_regex' => 'required|string|max:100',
        ]);

        $filterFlags = $request->input('filter_flags', 'aux');
        if (!preg_match('/^(aux|aux -T|x)$/', $filterFlags)) {
            abort(400, 'Invalid filter flags');
        }

        $commandRegex = $request->input('command_regex');

        $process = new Process(['ps', $filterFlags]);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        $output = $process->getOutput();
        $matchingProcesses = [];
        foreach (explode("\n", $output) as $line) {
            if (preg_match("/\s*(\d+)\s+.*($commandRegex)/", $line, $matches)) {
                $matchingProcesses[] = [
                    'processId' => (int)$matches[1],
                    'processString' => $line,
                ];
            }
        }

        return response()->json($matchingProcesses);
    }
}