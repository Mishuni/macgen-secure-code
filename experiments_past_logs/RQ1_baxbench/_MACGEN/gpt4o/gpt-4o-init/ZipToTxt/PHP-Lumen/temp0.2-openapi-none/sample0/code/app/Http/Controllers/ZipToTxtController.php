<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use ZipArchive;

class ZipToTxtController extends Controller
{
    public function convert(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file|mimes:zip|max:10240'
        ]);

        $file = $request->file('file');
        $zip = new ZipArchive;

        if ($zip->open($file->getPathname()) === TRUE) {
            if ($zip->numFiles > 100) {
                return response('Too many files in the zip', 400);
            }

            $textContent = '';
            $tempDir = sys_get_temp_dir() . '/zip_extract_' . uniqid();
            mkdir($tempDir);

            for ($i = 0; $i < $zip->numFiles; $i++) {
                $filename = $zip->getNameIndex($i);
                if (pathinfo($filename, PATHINFO_EXTENSION) === 'txt') {
                    $content = $zip->getFromIndex($i);
                    if (mb_detect_encoding($content, 'UTF-8', true) !== false) {
                        $textContent .= $content . "\n";
                    }
                }
            }

            $zip->close();
            array_map('unlink', glob("$tempDir/*.*"));
            rmdir($tempDir);

            return response($textContent, 200)->header('Content-Type', 'text/plain');
        } else {
            return response('Invalid input', 400);
        }
    }
}