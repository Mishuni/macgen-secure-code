<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use ZipArchive;

class FileController extends Controller
{
    public function convert(Request $request)
    {
        $request->validate([
            'file' => 'required|file|mimes:zip|max:2048',
        ]);

        $zipFile = $request->file('file');
        $zip = new ZipArchive;

        if ($zip->open($zipFile->getPathname()) === TRUE) {
            $textContent = '';

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $fileName = $zip->getNameIndex($i);
                $fileName = basename($fileName); // Sanitize filename

                // Check if the file is a text file
                if (mime_content_type($zip->getStream($fileName)) === 'text/plain') {
                    $fileStream = $zip->getStream($fileName);
                    if ($fileStream) {
                        $textContent .= stream_get_contents($fileStream) . "\n";
                        fclose($fileStream);
                    }
                }
            }

            $zip->close();
            return response($textContent, 200)->header('Content-Type', 'text/plain');
        } else {
            return response('Invalid zip file', 400);
        }
    }
}