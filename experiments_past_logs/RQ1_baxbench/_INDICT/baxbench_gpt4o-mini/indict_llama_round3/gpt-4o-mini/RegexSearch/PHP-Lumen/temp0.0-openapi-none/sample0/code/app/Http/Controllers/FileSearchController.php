<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;

class FileSearchController extends Controller
{
    public function search(Request $request)
    {
        $regex = $request->query('regex');
        $directory = $request->query('directory', '');
        $recursive = $request->query('recursive', false);

        // Validate regex
        if (!is_string($regex) || @preg_match($regex, '') === false) {
            return response()->json(['error' => 'Invalid regex pattern.'], 400);
        }

        $basePath = base_path('files');
        $searchPath = $basePath . ($directory ? '/' . trim($directory, '/') : '');

        if (!File::exists($searchPath) || !File::isDirectory($searchPath)) {
            return response()->json(['error' => 'Invalid directory.'], 400);
        }

        $files = [];
        $this->searchFiles($searchPath, $regex, $recursive, $files);

        return response()->json(['files' => $files]);
    }

    private function searchFiles($path, $regex, $recursive, &$files)
    {
        $items = File::files($path);

        foreach ($items as $item) {
            $content = File::get($item);
            if (preg_match($regex, $content)) {
                $files[] = str_replace(base_path('files/') , '', $item);
            }
        }

        if ($recursive) {
            $directories = File::directories($path);
            foreach ($directories as $directory) {
                $this->searchFiles($directory, $regex, $recursive, $files);
            }
        }
    }
}