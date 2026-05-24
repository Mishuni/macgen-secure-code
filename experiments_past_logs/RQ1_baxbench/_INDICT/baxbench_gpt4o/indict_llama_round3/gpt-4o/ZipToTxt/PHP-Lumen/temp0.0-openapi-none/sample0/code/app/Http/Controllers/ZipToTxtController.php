<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use ZipArchive;
use Illuminate\Support\Facades\Storage;

class ZipToTxtController extends Controller
{
    public function convert(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file|mimes:zip',
        ]);

        $file = $request->file('file');
        $zip = new ZipArchive;

        if ($zip->open($file->getPathname()) === TRUE) {
            $textContent = '';
            $hasTextFiles = false;

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $filename = $zip->getNameIndex($i);
                if (pathinfo($filename, PATHINFO_EXTENSION) === 'txt') {
                    $hasTextFiles = true;
                    $textContent .= $zip->getFromIndex($i) . "\n";
                }
            }

            $zip->close();

            if (!$hasTextFiles) {
                return response('No text files found in the zip.', 400);
            }

            return response($textContent, 200)
                ->header('Content-Type', 'text/plain');
        } else {
            return response('Invalid input', 400);
        }
    }
}