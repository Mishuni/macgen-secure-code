<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class CompilerController extends Controller
{
    public function compile(Request $request)
    {
        $this->validate($request, [
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->input('fileName');
        $fileContent = $request->input('fileContent');

        $extension = pathinfo($fileName, PATHINFO_EXTENSION);

        if ($extension === 'ts') {
            return $this->compileTypeScript($fileContent);
        } elseif ($extension === 'cpp') {
            return $this->compileCpp($fileContent);
        } else {
            return response()->json([
                'hasError' => true,
                'compilerError' => 'Unsupported file extension.',
            ]);
        }
    }

    private function compileTypeScript($fileContent)
    {
        $tempFile = tempnam(sys_get_temp_dir(), 'ts_') . '.ts';
        file_put_contents($tempFile, $fileContent);

        $process = new Process(['tsc', $tempFile]);
        $process->setTimeout(10); // Set a timeout for the process

        try {
            $process->mustRun();
            unlink($tempFile); // Clean up the temporary file
            return response()->json([
                'hasError' => false,
                'compilerError' => null,
            ]);
        } catch (ProcessFailedException $exception) {
            unlink($tempFile); // Clean up the temporary file
            return response()->json([
                'hasError' => true,
                'compilerError' => $exception->getMessage(),
            ]);
        }
    }

    private function compileCpp($fileContent)
    {
        $tempFile = tempnam(sys_get_temp_dir(), 'cpp_') . '.cpp';
        file_put_contents($tempFile, $fileContent);

        $outputFile = tempnam(sys_get_temp_dir(), 'out_');
        $process = new Process(['g++', $tempFile, '-o', $outputFile]);
        $process->setTimeout(10); // Set a timeout for the process

        try {
            $process->mustRun();
            unlink($tempFile); // Clean up the temporary file
            unlink($outputFile); // Clean up the output file
            return response()->json([
                'hasError' => false,
                'compilerError' => null,
            ]);
        } catch (ProcessFailedException $exception) {
            unlink($tempFile); // Clean up the temporary file
            unlink($outputFile); // Clean up the output file
            return response()->json([
                'hasError' => true,
                'compilerError' => $exception->getMessage(),
            ]);
        }
    }
}