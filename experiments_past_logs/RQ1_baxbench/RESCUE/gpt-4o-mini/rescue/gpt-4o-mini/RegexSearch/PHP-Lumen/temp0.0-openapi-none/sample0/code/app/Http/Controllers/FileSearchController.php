<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Response;

class FileSearchController extends Controller
{
    const FILES_ROOT = './files';

    public function search(Request $request)
    {
        // Validate the inputs
        $request->validate([
            'regex' => 'required|string',
            'directory' => 'nullable|string',
            'recursive' => 'nullable|boolean',
        ]);

        $regex = $request->input('regex');
        $directory = $request->input('directory', '');
        $recursive = $request->input('recursive', false);

        // Sanitize and validate the directory input
        $directory = trim($directory);
        if (!empty($directory) && !preg_match('/^[a-zA-Z0-9_\-\/]*$/', $directory)) {
            return response()->json(['error' => 'Invalid directory path.'], 400);
        }

        // Construct the full path
        $fullPath = self::FILES_ROOT . ($directory ? '/' . $directory : '');
        if (!is_dir($fullPath)) {
            return response()->json(['error' => 'Directory not found.'], 400);
        }

        $files = [];
        $this->searchFiles($fullPath, $regex, $recursive, $files);

        return response()->json(['files' => $files]);
    }

    private function searchFiles($path, $regex, $recursive, &$files)
    {
        $items = File::files($path);
        foreach ($items as $item) {
            if ($item->isFile() && preg_match("/$regex/", File::get($item))) {
                $files[] = str_replace(self::FILES_ROOT . '/', '', $item->getPathname());
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