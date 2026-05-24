<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;

class SongController extends Controller
{
    public function download(Request $request)
    {
        $this->validate($request, [
            'filename' => 'required|string'
        ]);

        $filename = basename($request->input('filename'));
        $filePath = realpath('/var/songs/' . $filename);

        if ($filePath === false || strpos($filePath, '/var/songs/') !== 0 || !file_exists($filePath)) {
            return response()->json(['error' => 'File does not exist'], 404);
        }

        return new StreamedResponse(function () use ($filePath) {
            readfile($filePath);
        }, 200, [
            'Content-Type' => 'audio/mpeg',
            'Content-Disposition' => 'attachment; filename="' . basename($filePath) . '"',
        ]);
    }
}