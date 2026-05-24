<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CompileController extends Controller
{
    public function compile(Request $request)
    {
        $request->validate([
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->fileName;
        $fileContent = $request->fileContent;

        // Validate file extension
        $allowedExtensions = ['ts', 'cpp'];
        if (!in_array(pathinfo($fileName, PATHINFO_EXTENSION), $allowedExtensions)) {
            return response()->json(['hasError' => true, 'compilerError' => 'Unsupported file type.']);
        }

        // Create a temporary file
        $tempFile = tempnam(sys_get_temp_dir(), 'code_') . '.' . pathinfo($fileName, PATHINFO_EXTENSION);
        file_put_contents($tempFile, $fileContent);

        $hasError = false;
        $compilerError = null;

        // Compile based on file extension
        if (pathinfo($tempFile, PATHINFO_EXTENSION) === 'ts') {
            $output = shell_exec("tsc " . escapeshellarg($tempFile) . " 2>&1");
            if ($output) {
                $hasError = true;
                $compilerError = $output;
            }
        } elseif (pathinfo($tempFile, PATHINFO_EXTENSION) === 'cpp') {
            $output = shell_exec("g++ " . escapeshellarg($tempFile) . " -o /dev/null 2>&1");
            if ($output) {
                $hasError = true;
                $compilerError = $output;
            }
        }

        // Clean up the temporary file
        unlink($tempFile);

        return response()->json([
            'hasError' => $hasError,
            'compilerError' => $compilerError,
        ]);
    }
}