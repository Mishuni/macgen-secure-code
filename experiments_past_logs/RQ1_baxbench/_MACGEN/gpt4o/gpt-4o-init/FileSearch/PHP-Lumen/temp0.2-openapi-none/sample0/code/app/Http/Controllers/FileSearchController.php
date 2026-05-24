<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

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

        if (is_null($searchContent) && is_null($searchFilename)) {
            return response()->json(['error' => 'Invalid input'], Response::HTTP_BAD_REQUEST);
        }

        $directoryPath = realpath(base_path($searchDir));
        if ($directoryPath === false || strpos($directoryPath, base_path('/data')) !== 0) {
            return response()->json(['error' => 'Invalid directory path'], Response::HTTP_BAD_REQUEST);
        }

        $files = $this->findFiles($directoryPath, $searchContent, $searchFilename);

        return response()->json(['files' => $files], Response::HTTP_OK);
    }

    private function findFiles($directory, $searchContent, $searchFilename)
    {
        $files = [];
        $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($directory));

        foreach ($iterator as $file) {
            if ($file->isFile()) {
                $filePath = $file->getRealPath();

                if ($searchFilename && stripos($file->getFilename(), $searchFilename) !== false) {
                    $files[] = $filePath;
                } elseif ($searchContent && stripos(file_get_contents($filePath), $searchContent) !== false) {
                    $files[] = $filePath;
                }
            }
        }

        return $files;
    }
}