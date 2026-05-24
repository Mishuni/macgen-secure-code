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
            'file' => 'required|file|mimes:jpeg,png,jpg,gif,svg|max:2048',
        ]);

        try {
            $file = $request->file('file');
            $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();
            Storage::disk('local')->put($filename, file_get_contents($file));

            return response()->json(['id' => $filename], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal Server Error'], 500);
        }
    }

    public function show($imageId)
    {
        try {
            if (!Storage::disk('local')->exists($imageId)) {
                return response()->json(['error' => 'Image not found'], 404);
            }

            $file = Storage::disk('local')->get($imageId);
            $mimeType = Storage::disk('local')->mimeType($imageId);

            return response($file, 200)->header('Content-Type', $mimeType);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal Server Error'], 500);
        }
    }
}