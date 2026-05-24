<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class SongController extends Controller
{
    private const SONGS_DIRECTORY = '/var/songs/';

    public function streamSong(Request $request)
    {
        $validated = $request->validate([
            'filename' => 'required|string',
        ]);

        $filename = basename($validated['filename']); // Prevent directory traversal
        $filePath = self::SONGS_DIRECTORY . $filename;

        if (!file_exists($filePath)) {
            return response()->json(['error' => 'File does not exist'], Response::HTTP_NOT_FOUND);
        }

        return response()->stream(function () use ($filePath) {
            $stream = fopen($filePath, 'rb');
            fpassthru($stream);
            fclose($stream);
        }, Response::HTTP_OK, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'inline; filename="' . $filename . '"',
        ]);
    }
}