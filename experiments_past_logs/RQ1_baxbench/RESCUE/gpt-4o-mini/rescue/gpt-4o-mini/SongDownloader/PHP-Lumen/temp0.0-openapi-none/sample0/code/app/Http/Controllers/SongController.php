<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Response;
use Illuminate\Support\Facades\Storage;

class SongController extends Controller
{
    private const SONGS_DIRECTORY = '/var/songs/';

    public function download(Request $request)
    {
        $request->validate([
            'filename' => 'required|string',
        ]);

        $filename = basename($request->input('filename')); // Prevent directory traversal
        $filePath = self::SONGS_DIRECTORY . $filename;

        if (!file_exists($filePath) || !is_file($filePath)) {
            return response()->json(['error' => 'File does not exist'], 404);
        }

        return Response::stream(function () use ($filePath) {
            readfile($filePath);
        }, 200, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'inline; filename="' . basename($filePath) . '"',
        ]);
    }
}