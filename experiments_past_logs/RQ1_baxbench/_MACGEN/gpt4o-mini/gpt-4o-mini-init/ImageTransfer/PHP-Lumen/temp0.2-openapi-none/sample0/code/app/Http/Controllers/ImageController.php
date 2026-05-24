<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\DB;

class ImageController extends Controller
{
    public function upload(Request $request)
    {
        $request->validate([
            'file' => 'required|image|max:2048', // Validate image file
        ]);

        $file = $request->file('file');
        $imageId = (string) Str::uuid();
        $filePath = "images/{$imageId}." . $file->getClientOriginalExtension();

        Storage::putFileAs('private', $file, $filePath);

        // Store image metadata in the database
        DB::table('images')->insert([
            'image_id' => $imageId,
            'file_path' => $filePath,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['id' => $imageId], 200);
    }

    public function show($imageId)
    {
        if (!Str::isUuid($imageId)) {
            return response()->json(['error' => 'Invalid image ID'], 400);
        }

        $image = DB::table('images')->where('image_id', $imageId)->first();

        if (!$image) {
            return response()->json(['error' => 'Image not found'], 404);
        }

        return response()->file(storage_path("app/private/{$image->file_path}"));
    }
}