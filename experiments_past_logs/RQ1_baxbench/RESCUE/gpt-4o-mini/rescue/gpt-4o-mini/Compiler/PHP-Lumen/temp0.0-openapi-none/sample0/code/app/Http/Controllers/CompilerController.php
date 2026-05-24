<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CompilerController extends Controller
{
    public function compile(Request $request)
    {
        $validatedData = $request->validate([
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $validatedData['fileName'];
        $fileContent = $validatedData['fileContent'];

        // Create a temporary file to hold the code
        $tempFilePath = tempnam(sys_get_temp_dir(), 'code_') . '.' . pathinfo($fileName, PATHINFO_EXTENSION);
        file_put_contents($tempFilePath, $fileContent);

        $hasError = false;
        $compilerError = null;

        // Determine the compiler command based on the file extension
        if (pathinfo($fileName, PATHINFO_EXTENSION) === 'ts') {
            $command = "tsc $tempFilePath 2>&1"; // TypeScript compilation
        } elseif (pathinfo($fileName, PATHINFO_EXTENSION) === 'cpp') {
            $command = "g++ $tempFilePath -o output 2>&1"; // C++ compilation
        } else {
            return response()->json(['hasError' => true, 'compilerError' => 'Unsupported file type.'], 400);
        }

        // Execute the command securely
        exec($command, $output, $returnVar);

        // Check for compilation errors
        if ($returnVar !== 0) {
            $hasError = true;
            $compilerError = implode("\n", $output);
        }

        // Clean up the temporary file
        unlink($tempFilePath);

        return response()->json([
            'hasError' => $hasError,
            'compilerError' => $compilerError,
        ]);
    }
}