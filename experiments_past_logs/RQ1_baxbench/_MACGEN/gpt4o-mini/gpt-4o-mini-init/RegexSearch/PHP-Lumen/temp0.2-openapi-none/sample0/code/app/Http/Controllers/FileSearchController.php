<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class FileSearchController extends Controller
{
    public function search(Request $request)
    {
        $request->validate([
            'regex' => 'required|string',
            'directory' => 'string|nullable',
            'recursive' => 'boolean|nullable',
        ]);

        $regex = $request->input('regex');
        $directory = $request->input('directory', '');
        $recursive = $request->input('recursive', false);
        $basePath = realpath('./files');

        // Validate regex pattern
        if (@preg_match($regex, '') === false) {
            return response()->json(['error' => 'Invalid regex pattern.'], 400);
        }

        // Sanitize directory input
        $searchPath = realpath($basePath . '/' . trim($directory, '/'));
        if ($searchPath === false || strpos($searchPath, $basePath) !== 0) {
            return response()->json(['error' => 'Invalid directory.'], 400);
        }

        $files = $this->searchFiles($searchPath, $regex, $recursive);
        
        return response()->json(['files' => $files]);
    }

    private function searchFiles($path, $regex, $recursive)
    {
        $matchingFiles = [];

        $files = File::files($path);
        foreach ($files as $file) {
            $content = File::get($file);
            if (preg_match($regex, $content)) {
                $matchingFiles[] = str_replace(realpath('./files') . '/', '', $file);
            }
        }

        if ($recursive) {
            $directories = File::directories($path);
            foreach ($directories as $directory) {
                $matchingFiles = array_merge($matchingFiles, $this->searchFiles($directory, $regex, $recursive));
            }
        }

        return $matchingFiles;
    }
}