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
            $hasTextFiles = false; // Flag to check if there are any text files

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $fileName = $zip->getNameIndex($i);
                $fileNameSanitized = basename($fileName); // Sanitize filename

                // Check if the file is a text file using the actual file path
                if (mime_content_type($zip->getStream($fileName)) === 'text/plain') {
                    if ($fileStream = $zip->getStream($fileName)) { // Check if the stream is valid
                        $textContent .= stream_get_contents($fileStream) . "\n";
                        fclose($fileStream);
                        $hasTextFiles = true; // Set flag if we found a text file
                    } else {
                        return response('Invalid text file stream', 400); // Handle invalid stream
                    }
                }
            }

            $zip->close();

            // If no text files were found, return a 400 response
            if (!$hasTextFiles) {
                return response('No text files found in the zip', 400);
            }

            return response($textContent, 200)->header('Content-Type', 'text/plain');
        } else {
            return response('Invalid zip file', 400);
        }
    }
}