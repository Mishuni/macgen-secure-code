<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class ImageController extends Controller
{
    public function upload(Request $request)
    {
        $request->validate([
            'file' => 'required|image|mimes:jpeg,png,jpg,gif,svg|max:2048',
        ]);

        $file = $request->file('file');
        $filename = Str::random(10) . '.' . $file->getClientOriginalExtension();
        $path = $file->storeAs('images', $filename, 'public');

        return response()->json(['id' => $filename], 200);
    }

    public function show($imageId)
    {
        $path = storage_path('app/public/images/' . $imageId);

        if (!file_exists($path)) {
            return response()->json(['error' => 'Image not found'], 404);
        }

        return response()->file($path, [
            'Content-Type' => mime_content_type($path),
            'Content-Disposition' => 'inline; filename="' . basename($path) . '"'
        ]);
    }
}