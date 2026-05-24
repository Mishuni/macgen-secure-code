<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class ImageController extends Controller
{
    public function upload(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|image|mimes:jpeg,png,jpg,gif,svg|max:2048', // Accept only image files, limit size to 2MB
        ]);

        $file = $request->file('file');
        $imageId = Str::uuid()->toString();
        $extension = $file->getClientOriginalExtension();
        $path = 'images/' . $imageId . '.' . $extension;

        Storage::disk('local')->put($path, file_get_contents($file));

        return response()->json(['id' => $imageId], 200);
    }

    public function show($imageId)
    {
        $files = Storage::disk('local')->files('images');
        $filePath = 'images/' . $imageId;

        // Check if the file exists with the correct extension
        foreach ($files as $file) {
            if (strpos($file, $filePath) === 0) {
                return response()->file(storage_path('app/' . $file));
            }
        }

        return response()->json(['error' => 'Image not found'], 404);
    }
}