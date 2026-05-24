<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class FileSearchController extends Controller
{
    public function search(Request $request)
    {
        $this->validate($request, [
            'search_content' => 'nullable|string',
            'search_filename' => 'nullable|string',
            'search_dir' => 'nullable|string',
        ]);

        $searchContent = $request->input('search_content');
        $searchFilename = $request->input('search_filename');
        $searchDir = $request->input('search_dir', '/data');

        // Sanitize the search directory to prevent directory traversal
        $baseDir = realpath(base_path('data'));
        $searchDir = realpath(base_path(trim($searchDir, '/')));

        if (!$searchDir || strpos($searchDir, $baseDir) !== 0) {
            return response()->json(['files' => []], 200);
        }

        $files = File::allFiles($searchDir);
        $matchedFiles = [];

        foreach ($files as $file) {
            $filePath = $file->getRealPath();
            $fileName = $file->getFilename();

            if ($searchFilename && stripos($fileName, $searchFilename) !== false) {
                $matchedFiles[] = $filePath;
                continue;
            }

            if ($searchContent) {
                $fileHandle = fopen($filePath, 'r');
                while (($line = fgets($fileHandle)) !== false) {
                    if (stripos($line, $searchContent) !== false) {
                        $matchedFiles[] = $filePath;
                        break;
                    }
                }
                fclose($fileHandle);
            }
        }

        return response()->json(['files' => $matchedFiles], 200);
    }
}