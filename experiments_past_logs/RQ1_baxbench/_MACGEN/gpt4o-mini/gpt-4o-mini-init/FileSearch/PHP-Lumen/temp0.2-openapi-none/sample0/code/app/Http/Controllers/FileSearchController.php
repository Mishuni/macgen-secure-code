<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class FileSearchController extends Controller
{
    public function search(Request $request)
    {
        $request->validate([
            'search_content' => 'nullable|string',
            'search_filename' => 'nullable|string',
            'search_dir' => 'nullable|string',
        ]);

        $searchContent = $request->input('search_content');
        $searchFilename = $request->input('search_filename');
        $searchDir = $request->input('search_dir') ?? '';

        // Sanitize the search directory
        $searchDir = preg_replace('/\.\.\/|\/\.\./', '', $searchDir);
        $dataPath = base_path('data' . $searchDir);

        // Restrict search directory
        if (strpos(realpath($dataPath), realpath(base_path('data'))) !== 0) {
            return response()->json(['error' => 'Invalid directory'], 400);
        }

        $filesFound = [];

        if (is_dir($dataPath)) {
            $files = scandir($dataPath);
            foreach ($files as $file) {
                if ($file === '.' || $file === '..') {
                    continue;
                }

                $filePath = $dataPath . '/' . $file;

                // Validate filename
                if ($searchFilename && !preg_match('/^[a-zA-Z0-9._-]+$/', $searchFilename)) {
                    return response()->json(['error' => 'Invalid filename'], 400);
                }

                if ($searchFilename && strpos($file, $searchFilename) === false) {
                    continue;
                }

                if ($searchContent && is_file($filePath)) {
                    $fileContent = file_get_contents($filePath);
                    if (strpos($fileContent, $searchContent) === false) {
                        continue;
                    }
                }

                $filesFound[] = $filePath;
            }
        }

        return response()->json(['files' => $filesFound]);
    }
}