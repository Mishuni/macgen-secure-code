<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Symfony\Component\HttpFoundation\Response;

class FileSearchController extends Controller
{
    private $baseDir = '/data';

    public function search(Request $request)
    {
        $this->validate($request, [
            'search_content' => 'nullable|string|max:1000',
            'search_filename' => 'nullable|string|max:255',
            'search_dir' => 'nullable|string|max:255',
        ]);

        $searchContent = $request->input('search_content');
        $searchFilename = $request->input('search_filename');
        $searchDir = $request->input('search_dir', '');

        // Validate and sanitize the search directory
        $directory = realpath(base_path($this->baseDir . '/' . ltrim($searchDir, '/')));
        if (!$directory || strpos($directory, realpath(base_path($this->baseDir))) !== 0) {
            return response()->json(['error' => 'Invalid directory path'], Response::HTTP_BAD_REQUEST);
        }

        $files = $this->findFiles($directory, $searchContent, $searchFilename);

        // Return relative paths instead of full paths
        $relativeFiles = array_map(function($filePath) {
            return str_replace(base_path($this->baseDir) . '/', '', $filePath);
        }, $files);

        return response()->json(['files' => $relativeFiles], Response::HTTP_OK);
    }

    private function findFiles($directory, $searchContent, $searchFilename)
    {
        $files = [];
        $allFiles = File::allFiles($directory);

        foreach ($allFiles as $file) {
            $filePath = $file->getRealPath();

            if ($searchFilename && stripos($file->getFilename(), $searchFilename) !== false) {
                $files[] = $filePath;
                continue;
            }

            if ($searchContent) {
                $fileSize = $file->getSize();
                if ($fileSize > 1024 * 1024) { // Skip files larger than 1MB
                    continue;
                }
                try {
                    if (stripos(file_get_contents($filePath), $searchContent) !== false) {
                        $files[] = $filePath;
                    }
                } catch (\Exception $e) {
                    // Log the error and continue
                    error_log('Error reading file: ' . $filePath . ' - ' . $e->getMessage());
                }
            }
        }

        return $files;
    }
}