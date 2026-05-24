<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use App\Models\Image;

class ImageController extends Controller
{
    public function upload(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file|mimes:jpeg,png,gif,bmp,tiff,webp|max:10240'
        ]);

        try {
            $file = $request->file('file');
            $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();
            $file->move(storage_path('app/public'), $filename);

            $image = new Image();
            $image->id = Str::uuid();
            $image->filename = $filename;
            $image->mime_type = $file->getClientMimeType();
            $image->save();

            return response()->json(['id' => $image->id], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }

    public function show($imageId)
    {
        try {
            $image = Image::findOrFail($imageId);
            $path = storage_path('app/public/' . $image->filename);

            if (!file_exists($path)) {
                return response()->json(['error' => 'Image not found'], 404);
            }

            return response()->file($path, [
                'Content-Type' => $image->mime_type,
                'Content-Disposition' => 'inline; filename="' . $image->filename . '"'
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json(['error' => 'Image not found'], 404);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }
}