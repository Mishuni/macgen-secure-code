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

        // Validate regex
        if (@preg_match($regex, null) === false) {
            return response()->json(['error' => 'Invalid regex pattern'], 400);
        }

        // Validate directory using realpath
        $baseDir = realpath(__DIR__ . '/../../../files');
        $searchDir = realpath($baseDir . '/' . $directory);

        // Ensure the directory is within the allowed base directory
        if ($searchDir === false || strpos($searchDir, $baseDir) !== 0) {
            return response()->json(['error' => 'Directory is not accessible'], 400);
        }

        $finder = new Finder();
        $finder->files()->in($searchDir);

        if ($recursive) {
            $finder->depth('>= 0');
        } else {
            $finder->depth('== 0');
        }

        $matchingFiles = [];
        foreach ($finder as $file) {
            // Limit file size to prevent DoS attacks
            if ($file->getSize() > 1024 * 1024) { // 1MB limit
                continue;
            }

            // Check file extension to prevent reading sensitive files
            $allowedExtensions = ['txt', 'log', 'md']; // Example whitelist
            if (!in_array($file->getExtension(), $allowedExtensions)) {
                continue;
            }

            // Use preg_match with a timeout to prevent regex DoS
            $content = file_get_contents($file->getRealPath());
            if ($this->safePregMatch("/$regex/", $content)) {
                $matchingFiles[] = str_replace($baseDir . '/', '', $file->getRealPath());
            }
        }

        return response()->json(['files' => $matchingFiles], 200);
    }

    private function safePregMatch($pattern, $subject)
    {
        $result = false;
        $timeout = 1; // 1 second timeout
        $start = microtime(true);

        try {
            $result = preg_match($pattern, $subject);
        } catch (\Exception $e) {
            return false;
        }

        if ((microtime(true) - $start) > $timeout) {
            return false;
        }

        return $result;
    }
}