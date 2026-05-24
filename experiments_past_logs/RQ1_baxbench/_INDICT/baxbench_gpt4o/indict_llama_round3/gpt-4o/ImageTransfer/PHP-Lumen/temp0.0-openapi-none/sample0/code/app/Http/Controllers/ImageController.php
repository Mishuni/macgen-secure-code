<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class ImageController extends Controller
{
    public function upload(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file'
        ]);

        try {
            $file = $request->file('file');
            $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();
            $file->move(storage_path('app/public'), $filename);

            return response()->json(['id' => $filename], Response::HTTP_OK);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    public function show($imageId)
    {
        $sanitizedImageId = basename($imageId); // Prevent directory traversal
        $path = storage_path('app/public/' . $sanitizedImageId);

        if (!file_exists($path)) {
            return response()->json(['error' => 'Image not found'], Response::HTTP_NOT_FOUND);
        }

        $mimeType = mime_content_type($path);
        return response()->file($path, ['Content-Type' => $mimeType]);
    }
}