<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Response;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        $request->validate([
            'images' => 'required|array',
            'images.*' => 'image|mimes:jpeg,png,gif,jpg|max:2048',
            'targetSize' => 'required|string',
            'delay' => 'integer|nullable',
            'appendReverted' => 'boolean|nullable',
        ]);

        $images = $request->file('images');
        $targetSize = $request->input('targetSize');
        $delay = $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        $tempDir = storage_path('app/temp');
        if (!is_dir($tempDir)) {
            mkdir($tempDir, 0755, true);
        }

        $imagePaths = [];
        foreach ($images as $image) {
            $path = $image->store('temp');
            $imagePaths[] = storage_path('app/' . $path);
        }

        if ($appendReverted) {
            $revertedImages = array_reverse($imagePaths);
            $imagePaths = array_merge($imagePaths, $revertedImages);
        }

        $gifPath = storage_path('app/gif_output.gif');
        $command = "convert -delay " . escapeshellarg($delay) . " -size " . escapeshellarg($targetSize) . " " . implode(' ', array_map('escapeshellarg', $imagePaths)) . " " . escapeshellarg($gifPath);

        exec($command, $output, $returnVar);
        if ($returnVar !== 0) {
            return response()->json(['error' => 'Failed to create GIF.'], 500);
        }

        return Response::download($gifPath)->deleteFileAfterSend(true);
    }
}