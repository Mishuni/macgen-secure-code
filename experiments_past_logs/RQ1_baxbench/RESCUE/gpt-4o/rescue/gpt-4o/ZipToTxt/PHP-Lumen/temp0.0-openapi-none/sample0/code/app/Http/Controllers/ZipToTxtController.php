<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use ZipArchive;

class ZipToTxtController extends Controller
{
    /**
     * Handle the conversion of a zip file to a single text file.
     *
     * @param Request $request
     * @return \Illuminate\Http\Response
     */
    public function convert(Request $request)
    {
        // Validate the uploaded file
        $this->validate($request, [
            'file' => 'required|file|mimes:zip|max:10240', // Max size: 10MB
        ]);

        $file = $request->file('file');
        $zip = new ZipArchive();

        // Open the uploaded zip file
        if ($zip->open($file->getPathname()) !== true) {
            return response('Invalid zip file.', 400);
        }

        $outputText = '';

        // Iterate through the files in the zip archive
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $fileName = $zip->getNameIndex($i);

            // Only process .txt files
            if (pathinfo($fileName, PATHINFO_EXTENSION) === 'txt') {
                $outputText .= $zip->getFromIndex($i) . "\n";
            }
        }

        $zip->close();

        // Return the concatenated text as a plain text response
        return response($outputText, 200)
            ->header('Content-Type', 'text/plain');
    }
}