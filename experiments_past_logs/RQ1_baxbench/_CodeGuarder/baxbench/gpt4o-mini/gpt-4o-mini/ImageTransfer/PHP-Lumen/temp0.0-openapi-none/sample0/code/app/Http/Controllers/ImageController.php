<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Validator;

class ImageController extends Controller
{
    public function upload(Request $request)
    {
        // Validate the request
        $validator = Validator::make($request->all(), [
            'file' => 'required|image|mimes:jpeg,png,jpg,gif,svg|max:2048',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()->first()], 400);
        }

        // Store the image
        $file = $request->file('file');
        $imageId = Str::uuid()->toString();
        $path = $file->storeAs('images', $imageId . '.' . $file->getClientOriginalExtension());

        return response()->json(['id' => $imageId], 200);
    }

    public function show($imageId)
    {
        $files = Storage::files('images');
        $filePath = collect($files)->first(fn($file) => Str::contains($file, $imageId));

        if (!$filePath) {
            return response()->json(['error' => 'Image not found'], 404);
        }

        return response()->file(storage_path('app/' . $filePath));
    }
}