<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Response;

class SongController extends Controller
{
    public function download(Request $request)
    {
        $request->validate([
            'filename' => 'required|string',
        ]);

        $filename = $request->input('filename');

        // Validate filename to prevent path traversal
        if (!preg_match('/^[a-zA-Z0-9_\-\.]+\.mp3$/', $filename)) {
            return response()->json(['error' => 'Invalid filename'], 400);
        }

        // Construct the full file path
        $filePath = realpath('/var/songs/' . basename($filename));

        // Check if the file exists and is within the allowed directory
        if (strpos($filePath, '/var/songs/') !== 0 || !file_exists($filePath)) {
            return response()->json(['error' => 'File does not exist'], 404);
        }

        // Stream the file content
        return Response::stream(function () use ($filePath) {
            readfile($filePath);
        }, 200, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'inline; filename="' . basename($filePath) . '"',
        ]);
    }
}