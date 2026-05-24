<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class CompileController extends Controller
{
    public function compile(Request $request)
    {
        $this->validate($request, [
            'fileName' => 'required|string|regex:/^[a-zA-Z0-9_\-]+\.(ts|cpp)$/',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->input('fileName');
        $fileContent = $request->input('fileContent');
        $extension = pathinfo($fileName, PATHINFO_EXTENSION);
        $filePath = sys_get_temp_dir() . '/' . uniqid('code_', true) . '.' . $extension;

        file_put_contents($filePath, $fileContent);

        $command = $this->getCompileCommand($extension, $filePath);

        if (!$command) {
            return response()->json([
                'hasError' => true,
                'compilerError' => 'Unsupported file type.'
            ]);
        }

        $process = Process::fromShellCommandline($command);
        $process->run();

        if (!$process->isSuccessful()) {
            return response()->json([
                'hasError' => true,
                'compilerError' => $process->getErrorOutput()
            ]);
        }

        return response()->json([
            'hasError' => false,
            'compilerError' => null
        ]);
    }

    private function getCompileCommand($extension, $filePath)
    {
        switch ($extension) {
            case 'ts':
                return escapeshellcmd("tsc " . escapeshellarg($filePath));
            case 'cpp':
                return escapeshellcmd("g++ " . escapeshellarg($filePath) . " -o " . escapeshellarg(sys_get_temp_dir() . "/output"));
            default:
                return null;
        }
    }
}