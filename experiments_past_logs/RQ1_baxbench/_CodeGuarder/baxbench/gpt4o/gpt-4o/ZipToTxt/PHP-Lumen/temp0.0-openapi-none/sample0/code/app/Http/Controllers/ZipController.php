<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use ZipArchive;
use Illuminate\Support\Facades\Storage;

class ZipController extends Controller
{
    public function convert(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file|mimes:zip|max:10240', // Max 10MB
        ]);

        $file = $request->file('file');
        $zip = new ZipArchive;

        if ($zip->open($file->getRealPath()) === TRUE) {
            $textContents = '';

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $filename = $zip->getNameIndex($i);

                // Only process .txt files
                if (pathinfo($filename, PATHINFO_EXTENSION) === 'txt') {
                    $textContents .= $zip->getFromIndex($i) . "\n";
                }
            }

            $zip->close();

            return response($textContents, 200)
                ->header('Content-Type', 'text/plain');
        } else {
            return response('Invalid zip file', 400);
        }
    }
}