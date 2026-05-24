<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CompilerController extends Controller
{
    public function compile(Request $request)
    {
        $request->validate([
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->input('fileName');
        $fileContent = $request->input('fileContent');

        // Determine the file type based on the file extension
        $extension = pathinfo($fileName, PATHINFO_EXTENSION);
        $hasError = false;
        $compilerError = null;

        // Create a temporary file for the code
        $tempFile = tempnam(sys_get_temp_dir(), 'code_') . '.' . $extension;
        file_put_contents($tempFile, $fileContent);

        // Compile based on the file type
        if ($extension === 'ts') {
            $output = [];
            $returnVar = 0;
            exec("tsc $tempFile 2>&1", $output, $returnVar);
            if ($returnVar !== 0) {
                $hasError = true;
                $compilerError = implode("\n", $output);
            }
        } elseif ($extension === 'cpp') {
            $output = [];
            $returnVar = 0;
            exec("g++ $tempFile -o /dev/null 2>&1", $output, $returnVar);
            if ($returnVar !== 0) {
                $hasError = true;
                $compilerError = implode("\n", $output);
            }
        } else {
            $hasError = true;
            $compilerError = "Unsupported file type.";
        }

        // Clean up the temporary file
        unlink($tempFile);

        return response()->json([
            'hasError' => $hasError,
            'compilerError' => $compilerError,
        ]);
    }
}