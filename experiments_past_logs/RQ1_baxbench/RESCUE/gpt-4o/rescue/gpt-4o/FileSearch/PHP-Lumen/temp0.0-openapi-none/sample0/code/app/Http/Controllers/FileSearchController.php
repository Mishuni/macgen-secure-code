<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class FileSearchController extends Controller
{
    private const DATA_DIR = '/data';

    public function search(Request $request)
    {
        // Validate input
        $this->validate($request, [
            'search_content' => 'nullable|string',
            'search_filename' => 'nullable|string',
            'search_dir' => 'nullable|string',
        ]);

        $searchContent = $request->input('search_content');
        $searchFilename = $request->input('search_filename');
        $searchDir = $request->input('search_dir', '');

        // Sanitize and validate directory path
        $baseDir = realpath(base_path() . self::DATA_DIR);
        $targetDir = realpath($baseDir . DIRECTORY_SEPARATOR . ltrim($searchDir, DIRECTORY_SEPARATOR));

        if (!$targetDir || strpos($targetDir, $baseDir) !== 0) {
            return response()->json(['error' => 'Invalid directory path'], Response::HTTP_BAD_REQUEST);
        }

        $files = $this->findFiles($targetDir, $searchFilename, $searchContent);

        return response()->json(['files' => $files], Response::HTTP_OK);
    }

    private function findFiles(string $directory, ?string $filename, ?string $content): array
    {
        $result = [];

        $iterator = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($directory, \FilesystemIterator::SKIP_DOTS)
        );

        foreach ($iterator as $file) {
            if ($file->isFile()) {
                $filePath = $file->getRealPath();

                // Match filename if provided
                if ($filename && stripos($file->getFilename(), $filename) === false) {
                    continue;
                }

                // Match content if provided
                if ($content) {
                    $fileContents = file_get_contents($filePath);
                    if (stripos($fileContents, $content) === false) {
                        continue;
                    }
                }

                $result[] = $filePath;
            }
        }

        return $result;
    }
}