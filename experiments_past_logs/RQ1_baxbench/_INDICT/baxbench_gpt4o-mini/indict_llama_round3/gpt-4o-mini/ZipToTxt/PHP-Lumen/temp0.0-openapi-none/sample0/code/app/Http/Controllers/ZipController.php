<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use ZipArchive;

class ZipController extends Controller
{
    public function convert(Request $request)
    {
        $request->validate([
            'file' => 'required|file|mimes:zip|max:2048', // Limit file size to 2MB
        ]);

        $zipFile = $request->file('file');
        $zip = new ZipArchive;

        if ($zip->open($zipFile->getPathname()) === TRUE) {
            $textContent = '';

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $fileName = $zip->getNameIndex($i);
                if (pathinfo($fileName, PATHINFO_EXTENSION) === 'txt') {
                    $fileContent = $zip->getFromIndex($i);
                    if ($fileContent !== false) {
                        $textContent .= $fileContent . "\n";
                    }
                }
            }

            $zip->close();

            if (empty($textContent)) {
                return response('No text files found in the zip.', 400);
            }

            return response($textContent, 200)
                ->header('Content-Type', 'text/plain');
        } else {
            return response('Invalid zip file', 400);
        }
    }
}