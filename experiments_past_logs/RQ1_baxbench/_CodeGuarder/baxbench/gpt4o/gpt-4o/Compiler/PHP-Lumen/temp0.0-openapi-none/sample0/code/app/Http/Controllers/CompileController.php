<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class CompileController extends Controller
{
    public function compile(Request $request)
    {
        $this->validate($request, [
            'fileName' => 'required|string',
            'fileContent' => 'required|string',
        ]);

        $fileName = $request->input('fileName');
        $fileContent = $request->input('fileContent');

        $fileExtension = pathinfo($fileName, PATHINFO_EXTENSION);

        if ($fileExtension === 'ts') {
            $compiler = 'tsc';
        } elseif ($fileExtension === 'cpp') {
            $compiler = 'g++';
        } else {
            return response()->json([
                'hasError' => true,
                'compilerError' => 'Unsupported file type.'
            ]);
        }

        $tempFilePath = sys_get_temp_dir() . '/' . $fileName;
        file_put_contents($tempFilePath, $fileContent);

        $process = new Process([$compiler, $tempFilePath]);
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
}