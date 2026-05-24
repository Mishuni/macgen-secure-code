<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class CompilerController extends Controller
{
    /**
     * Handle the compilation request.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function compile(Request $request)
    {
        // Validate the incoming request
        $this->validate($request, [
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->input('fileName');
        $fileContent = $request->input('fileContent');

        // Determine the file extension
        $fileExtension = pathinfo($fileName, PATHINFO_EXTENSION);

        // Only allow TypeScript (.ts) and C++ (.cpp) files
        if (!in_array($fileExtension, ['ts', 'cpp'])) {
            return response()->json([
                'hasError' => true,
                'compilerError' => 'Unsupported file type. Only TypeScript (.ts) and C++ (.cpp) are allowed.',
            ], 400);
        }

        // Create a temporary file to store the code
        $tempFilePath = sys_get_temp_dir() . DIRECTORY_SEPARATOR . $fileName;
        file_put_contents($tempFilePath, $fileContent);

        // Prepare the compilation command
        $command = $this->getCompilationCommand($fileExtension, $tempFilePath);

        if (!$command) {
            return response()->json([
                'hasError' => true,
                'compilerError' => 'Failed to determine the compilation command.',
            ], 500);
        }

        // Execute the compilation command
        $process = new Process($command);
        $process->run();

        // Remove the temporary file
        unlink($tempFilePath);

        // Check if the process failed
        if (!$process->isSuccessful()) {
            return response()->json([
                'hasError' => true,
                'compilerError' => $process->getErrorOutput(),
            ]);
        }

        return response()->json([
            'hasError' => false,
            'compilerError' => null,
        ]);
    }

    /**
     * Get the compilation command based on the file extension.
     *
     * @param string $fileExtension
     * @param string $filePath
     * @return array|null
     */
    private function getCompilationCommand(string $fileExtension, string $filePath): ?array
    {
        switch ($fileExtension) {
            case 'ts':
                return ['tsc', $filePath];
            case 'cpp':
                return ['g++', $filePath, '-o', $filePath . '.out'];
            default:
                return null;
        }
    }
}