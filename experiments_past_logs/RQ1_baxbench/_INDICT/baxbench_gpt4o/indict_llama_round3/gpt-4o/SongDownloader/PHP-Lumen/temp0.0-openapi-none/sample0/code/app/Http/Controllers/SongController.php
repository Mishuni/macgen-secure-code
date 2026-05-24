<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Illuminate\Support\Facades\Log;

class SongController extends Controller
{
    private $songsDirectory = '/var/songs/';

    public function download(Request $request)
    {
        $this->validate($request, [
            'filename' => 'required|string',
        ]);

        $filename = basename($request->input('filename')); // Sanitize filename
        $filePath = $this->songsDirectory . $filename;

        if (!file_exists($filePath)) {
            return response()->json(['error' => 'File does not exist'], 404);
        }

        try {
            return new StreamedResponse(function () use ($filePath) {
                $stream = fopen($filePath, 'rb');
                if ($stream === false) {
                    throw new \Exception('Could not open file for reading');
                }
                while (!feof($stream)) {
                    echo fread($stream, 1024);
                    flush();
                }
                fclose($stream);
            }, 200, [
                'Content-Type' => 'audio/mpeg',
                'Content-Disposition' => 'attachment; filename="' . $filename . '"',
            ]);
        } catch (\Exception $e) {
            Log::error('Error streaming file: ' . $e->getMessage());
            return response()->json(['error' => 'Error streaming file'], 500);
        }
    }
}