<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Finder\Finder;

class FileSearchController extends Controller
{
    private const FILES_ROOT = __DIR__ . '/../../../files';

    public function search(Request $request)
    {
        try {
            // Validate input
            $regex = $request->query('regex');
            $directory = $request->query('directory', '');
            $recursive = filter_var($request->query('recursive', false), FILTER_VALIDATE_BOOLEAN);

            if (empty($regex)) {
                return response()->json(['error' => 'The regex parameter is required.'], 400);
            }

            // Sanitize and validate directory
            $safeDirectory = realpath(self::FILES_ROOT . '/' . $directory);
            if ($safeDirectory === false || strpos($safeDirectory, realpath(self::FILES_ROOT)) !== 0) {
                return response()->json(['error' => 'Invalid or inaccessible directory.'], 400);
            }

            // Compile regex
            if (@preg_match($regex, '') === false) {
                return response()->json(['error' => 'Malformed regex pattern.'], 400);
            }

            // Search files
            $finder = new Finder();
            $finder->files()->in($safeDirectory);

            if (!$recursive) {
                $finder->depth('== 0');
            }

            $matchingFiles = [];
            foreach ($finder as $file) {
                $content = file_get_contents($file->getRealPath());
                if (preg_match("/$regex/", $content)) {
                    $relativePath = str_replace(self::FILES_ROOT . '/', '', $file->getRealPath());
                    $matchingFiles[] = $relativePath;
                }
            }

            return response()->json(['files' => $matchingFiles], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error.'], 500);
        }
    }
}