<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class FileSearchController extends Controller
{
    const DATA_DIR = '/data';

    public function search(Request $request)
    {
        // Validate input
        $request->validate([
            'search_content' => 'nullable|string',
            'search_filename' => 'nullable|string',
            'search_dir' => 'nullable|string',
        ]);

        $searchContent = $request->input('search_content');
        $searchFilename = $request->input('search_filename');
        $searchDir = $request->input('search_dir');

        // Sanitize and validate the search directory
        if ($searchDir) {
            $searchDir = trim($searchDir, '/');
            if (preg_match('/[^a-zA-Z0-9_\-\/]/', $searchDir)) {
                return response()->json(['error' => 'Invalid directory name'], 400);
            }
        }

        $files = $this->findFiles($searchContent, $searchFilename, $searchDir);

        return response()->json(['files' => $files]);
    }

    private function findFiles($content, $filename, $dir)
    {
        $files = [];
        $baseDir = base_path(self::DATA_DIR);

        // Construct the full directory path
        $fullDir = $baseDir . ($dir ? '/' . $dir : '');

        // Check if the directory exists
        if (File::exists($fullDir) && File::isDirectory($fullDir)) {
            $allFiles = File::allFiles($fullDir);

            foreach ($allFiles as $file) {
                $filePath = $file->getRealPath();
                $fileName = $file->getFilename();

                // Check filename match
                if ($filename && !str_contains($fileName, $filename)) {
                    continue;
                }

                // Check content match
                if ($content) {
                    $fileContent = File::get($filePath);
                    if (!str_contains($fileContent, $content)) {
                        continue;
                    }
                }

                $files[] = $filePath;
            }
        }

        return $files;
    }
}