<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Response;

class SongController extends Controller
{
    private $songDirectory = '/var/songs/';

    public function download(Request $request)
    {
        $request->validate([
            'filename' => 'required|string|regex:/^[a-zA-Z0-9_\-\.]+$/', // Allow only specific characters
        ]);

        $filename = $request->input('filename');
        $filePath = $this->songDirectory . $filename;

        // Check if the file exists and is a file
        if (!file_exists($filePath) || !is_file($filePath)) {
            return response()->json(['error' => 'File does not exist'], 404);
        }

        // Check for file extension
        $fileExtension = pathinfo($filePath, PATHINFO_EXTENSION);
        if (strtolower($fileExtension) !== 'mp3') {
            return response()->json(['error' => 'Unsupported file type'], 400);
        }

        return Response::stream(function () use ($filePath) {
            $stream = fopen($filePath, 'rb');
            fpassthru($stream);
            fclose($stream);
        }, 200, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'inline; filename="' . basename($filePath) . '"',
        ]);
    }
}