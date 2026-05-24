<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CompilationController extends Controller
{
    public function compile(Request $request)
    {
        $request->validate([
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->input('fileName');
        $fileContent = $request->input('fileContent');

        // Save the file temporarily
        $tempFilePath = sys_get_temp_dir() . '/' . $fileName;
        file_put_contents($tempFilePath, $fileContent);

        // Determine the file extension
        $extension = pathinfo($fileName, PATHINFO_EXTENSION);
        $compilerCommand = '';

        if ($extension === 'ts') {
            $compilerCommand = "tsc $tempFilePath 2>&1"; // TypeScript compilation
        } elseif ($extension === 'cpp') {
            $compilerCommand = "g++ $tempFilePath -o " . sys_get_temp_dir() . '/output 2>&1'; // C++ compilation
        } else {
            return response()->json(['hasError' => true, 'compilerError' => 'Unsupported file type.'], 400);
        }

        // Execute the compiler command
        $output = [];
        $returnVar = 0;
        exec($compilerCommand, $output, $returnVar);

        // Clean up the temporary file
        unlink($tempFilePath);

        if ($returnVar !== 0) {
            return response()->json(['hasError' => true, 'compilerError' => implode("\n", $output)], 200);
        }

        return response()->json(['hasError' => false, 'compilerError' => null], 200);
    }
}