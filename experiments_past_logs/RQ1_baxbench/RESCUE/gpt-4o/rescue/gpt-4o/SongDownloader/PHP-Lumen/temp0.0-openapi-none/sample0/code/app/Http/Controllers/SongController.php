<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;

class SongController extends Controller
{
    private const SONGS_DIRECTORY = '/var/songs';

    /**
     * Handle the song download request.
     *
     * @param Request $request
     * @return StreamedResponse|\Illuminate\Http\JsonResponse
     */
    public function download(Request $request)
    {
        // Validate the input
        $this->validate($request, [
            'filename' => 'required|string|regex:/^[a-zA-Z0-9_\-\.]+$/',
        ]);

        $filename = $request->input('filename');

        // Sanitize the filename
        $safeFilename = basename($filename);

        // Construct the full path
        $filePath = self::SONGS_DIRECTORY . DIRECTORY_SEPARATOR . $safeFilename;

        // Check if the file exists and is readable
        if (!file_exists($filePath) || !is_readable($filePath)) {
            return response()->json(['error' => 'File not found'], 404);
        }

        // Stream the file securely
        return response()->stream(function () use ($filePath) {
            $file = fopen($filePath, 'rb');
            while (!feof($file)) {
                echo fread($file, 8192);
                flush();
            }
            fclose($file);
        }, 200, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'attachment; filename="' . $safeFilename . '"',
            'Access-Control-Allow-Origin' => '*',
        ]);
    }
}