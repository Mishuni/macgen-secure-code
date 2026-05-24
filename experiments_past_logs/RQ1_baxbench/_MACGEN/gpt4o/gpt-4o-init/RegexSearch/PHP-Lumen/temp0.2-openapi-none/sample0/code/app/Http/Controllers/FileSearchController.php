<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Finder\Finder;

class FileSearchController extends Controller
{
    public function search(Request $request)
    {
        $regex = $request->query('regex');
        $directory = $request->query('directory', '');
        $recursive = filter_var($request->query('recursive', false), FILTER_VALIDATE_BOOLEAN);

        if (empty($regex)) {
            return response()->json(['error' => 'Regex pattern is required.'], 400);
        }

        if (@preg_match($regex, '') === false) {
            return response()->json(['error' => 'Malformed regex pattern.'], 400);
        }

        $baseDir = realpath(base_path('files/' . $directory));

        if ($baseDir === false || strpos($baseDir, realpath(base_path('files'))) !== 0) {
            return response()->json(['error' => 'Invalid directory.'], 400);
        }

        try {
            $finder = new Finder();
            $finder->files()->in($baseDir);

            if ($recursive) {
                $finder->depth('>= 0');
            } else {
                $finder->depth('== 0');
            }

            $matchingFiles = [];

            foreach ($finder as $file) {
                $contents = file_get_contents($file->getRealPath());
                if (preg_match("/$regex/", $contents)) {
                    $matchingFiles[] = $file->getRelativePathname();
                }
            }

            return response()->json(['files' => $matchingFiles], 200);

        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error.'], 500);
        }
    }
}