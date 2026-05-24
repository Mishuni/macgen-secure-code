<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Validator;

class FileSearchController extends Controller
{
    private $dataDirectory = '/data';

    public function search(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'search_content' => 'nullable|string',
            'search_filename' => 'nullable|string',
            'search_dir' => 'nullable|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $searchContent = $request->input('search_content');
        $searchFilename = $request->input('search_filename');
        $searchDir = $request->input('search_dir', '');

        $files = $this->findFiles($searchContent, $searchFilename, $searchDir);

        return response()->json(['files' => $files]);
    }

    private function findFiles($content, $filename, $dir)
    {
        $files = [];
        $fullPath = base_path($this->dataDirectory . $dir);

        if (File::exists($fullPath) && File::isDirectory($fullPath)) {
            $allFiles = File::allFiles($fullPath);

            foreach ($allFiles as $file) {
                $filePath = $file->getRealPath();
                $fileName = $file->getFilename();

                if (($filename && fnmatch($filename, $fileName)) || 
                    ($content && str_contains(File::get($filePath), $content))) {
                    $files[] = $filePath;
                }
            }
        }

        return $files;
    }
}