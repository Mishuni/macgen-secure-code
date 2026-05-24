<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use ZipArchive;

class ZipController extends Controller
{
    public function convert(Request $request)
    {
        $request->validate([
            'file' => 'required|file|mimes:zip|max:2048', // Validate file type and size
        ]);

        $zipFile = $request->file('file');
        $zip = new ZipArchive;

        if ($zip->open($zipFile->getPathname()) === TRUE) {
            $contents = '';

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $filename = $zip->getNameIndex($i);
                if (pathinfo($filename, PATHINFO_EXTENSION) === 'txt') {
                    $contents .= $zip->getFromIndex($i) . "\n"; // Concatenate text file contents
                }
            }

            $zip->close();

            return response($contents, 200)
                ->header('Content-Type', 'text/plain');
        } else {
            return response()->json(['error' => 'Invalid zip file'], 400);
        }
    }
}