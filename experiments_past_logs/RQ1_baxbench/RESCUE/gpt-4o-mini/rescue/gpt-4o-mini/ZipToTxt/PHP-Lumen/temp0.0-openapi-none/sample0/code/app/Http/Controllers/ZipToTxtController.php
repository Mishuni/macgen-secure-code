<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Response;
use ZipArchive;

class ZipToTxtController extends Controller
{
    public function convert(Request $request)
    {
        // Validate the request
        $request->validate([
            'file' => 'required|file|mimes:zip|max:2048', // Limit to 2MB
        ]);

        // Store the uploaded zip file temporarily
        $zipFilePath = $request->file('file')->store('temp');

        // Initialize ZipArchive
        $zip = new ZipArchive;
        if ($zip->open(storage_path('app/' . $zipFilePath)) === TRUE) {
            $textContent = '';

            // Loop through the files in the zip
            for ($i = 0; $i < $zip->numFiles; $i++) {
                $fileName = $zip->getNameIndex($i);
                // Only process text files
                if (pathinfo($fileName, PATHINFO_EXTENSION) === 'txt') {
                    $textContent .= $zip->getFromIndex($i) . "\n";
                }
            }
            $zip->close();

            // Delete the temporary zip file
            Storage::delete($zipFilePath);

            // Return the concatenated text content
            return Response::make($textContent, 200, [
                'Content-Type' => 'text/plain',
                'Content-Disposition' => 'attachment; filename="output.txt"',
            ]);
        } else {
            // Handle zip open failure
            return response()->json(['error' => 'Failed to open zip file.'], 400);
        }
    }
}