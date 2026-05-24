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

        // Validate regex pattern
        if (@preg_match("/$regex/", null) === false) {
            return response()->json(['error' => 'Malformed regex pattern.'], 400);
        }

        // Sanitize directory input
        $directory = trim($directory, '/');
        if (strpos($directory, '..') !== false) {
            return response()->json(['error' => 'Invalid directory path.'], 400);
        }

        $baseDir = base_path('files/' . $directory);

        if (!is_dir($baseDir)) {
            return response()->json(['error' => 'Directory not found or inaccessible.'], 400);
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
                $content = $file->getContents();
                $startTime = microtime(true);
                if (preg_match("/$regex/", $content)) {
                    $endTime = microtime(true);
                    if (($endTime - $startTime) > 1) { // Timeout after 1 second
                        return response()->json(['error' => 'Regex evaluation timeout.'], 400);
                    }
                    $relativePath = str_replace(base_path('files/'), '', $file->getRealPath());
                    $matchingFiles[] = $relativePath;
                }
            }

            return response()->json(['files' => $matchingFiles], 200);

        } catch (\Exception $e) {
            return response()->json(['error' => 'An error occurred while processing your request.'], 500);
        }
    }
}