<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\File;
use Symfony\Component\Finder\Finder;

class FileSearchController extends Controller
{
    public function search(Request $request)
    {
        $regex = $request->query('regex');
        $directory = $request->query('directory', '');
        $recursive = filter_var($request->query('recursive', false), FILTER_VALIDATE_BOOLEAN);

        if (empty($regex)) {
            return response()->json(['error' => 'Regex pattern is required'], 400);
        }

        $baseDir = base_path('files');
        $searchDir = realpath($baseDir . DIRECTORY_SEPARATOR . $directory);

        if ($searchDir === false || strpos($searchDir, $baseDir) !== 0) {
            return response()->json(['error' => 'Invalid directory path'], 400);
        }

        try {
            $finder = new Finder();
            $finder->files()->in($searchDir);

            if (!$recursive) {
                $finder->depth('== 0');
            }

            $matchingFiles = [];
            foreach ($finder as $file) {
                if (preg_match("/$regex/", $file->getContents())) {
                    $relativePath = str_replace($baseDir . DIRECTORY_SEPARATOR, '', $file->getRealPath());
                    $matchingFiles[] = $relativePath;
                }
            }

            return response()->json(['files' => $matchingFiles], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }
}