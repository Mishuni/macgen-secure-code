<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

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

        // Sanitize the search_dir input to prevent directory traversal
        $searchDir = trim($searchDir, '/');
        $dataPath = base_path('data/' . $searchDir);

        $filesFound = [];

        // Check if the directory exists and is indeed a directory
        if (File::exists($dataPath) && File::isDirectory($dataPath)) {
            $files = File::allFiles($dataPath);

            foreach ($files as $file) {
                $filePath = $file->getRealPath();
                $fileName = $file->getFilename();

                // Check for filename match or content match
                if (($searchFilename && strpos($fileName, $searchFilename) !== false) ||
                    ($searchContent && strpos(File::get($filePath), $searchContent) !== false)) {
                    $filesFound[] = $filePath;
                }
            }
        }

        return response()->json(['files' => $filesFound]);
    }
}