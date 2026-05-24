<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;

class SongController extends Controller
{
    private $songsDirectory = '/var/songs';

    public function download(Request $request)
    {
        $this->validate($request, [
            'filename' => 'required|string',
        ]);

        $filename = basename($request->input('filename'));
        $filePath = $this->songsDirectory . DIRECTORY_SEPARATOR . $filename;

        if (!file_exists($filePath)) {
            return response()->json(['error' => 'File does not exist'], 404);
        }

        return new StreamedResponse(function () use ($filePath) {
            $stream = fopen($filePath, 'rb');
            fpassthru($stream);
            fclose($stream);
        }, 200, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'inline; filename="' . $filename . '"',
        ]);
    }
}