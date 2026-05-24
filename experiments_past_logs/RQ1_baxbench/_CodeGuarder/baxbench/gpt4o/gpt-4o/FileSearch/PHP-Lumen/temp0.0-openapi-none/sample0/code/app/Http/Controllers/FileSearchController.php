<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Response;

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

        $baseDir = base_path($searchDir);
        if (!File::exists($baseDir) || !File::isDirectory($baseDir)) {
            return Response::json(['files' => []], 200);
        }

        $files = $this->findFiles($baseDir, $searchContent, $searchFilename);

        return Response::json(['files' => $files], 200);
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