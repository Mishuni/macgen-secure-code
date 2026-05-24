<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Response;

class FileSearchController extends Controller
{
    private const FILES_ROOT = './files';

    public function search(Request $request)
    {
        $regex = $request->query('regex');
        $directory = $request->query('directory', '');
        $recursive = $request->query('recursive', false);

        // Validate regex
        if (@preg_match($regex, '') === false) {
            return Response::json(['error' => 'Invalid regex pattern.'], 400);
        }

        $searchPath = self::FILES_ROOT . '/' . trim($directory, '/');
        if (!File::exists($searchPath) || !File::isDirectory($searchPath)) {
            return Response::json(['error' => 'Invalid directory.'], 400);
        }

        $files = $this->searchFiles($searchPath, $regex, $recursive);
        return Response::json(['files' => $files]);
    }

    private function searchFiles($path, $regex, $recursive)
    {
        $matches = [];
        $files = File::files($path);

        foreach ($files as $file) {
            $content = File::get($file);
            if (preg_match($regex, $content)) {
                $matches[] = str_replace(self::FILES_ROOT . '/', '', $file->getPathname());
            }
        }

        if ($recursive) {
            $directories = File::directories($path);
            foreach ($directories as $directory) {
                $matches = array_merge($matches, $this->searchFiles($directory, $regex, $recursive));
            }
        }

        return $matches;
    }
}