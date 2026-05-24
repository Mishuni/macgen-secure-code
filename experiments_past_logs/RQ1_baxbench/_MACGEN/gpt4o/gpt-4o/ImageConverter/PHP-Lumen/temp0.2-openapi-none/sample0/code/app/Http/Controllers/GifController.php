<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        $this->validate($request, [
            'images' => 'required|array',
            'images.*' => 'required|file|image',
            'targetSize' => 'required|string|regex:/^\d+x\d+$/',
            'delay' => 'integer|min:1',
            'appendReverted' => 'boolean',
        ]);

        $images = $request->file('images');
        $targetSize = $request->input('targetSize');
        $delay = $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        $imagePaths = [];
        foreach ($images as $image) {
            $path = $image->store('temp');
            $imagePaths[] = storage_path('app/' . $path);
        }

        if ($appendReverted) {
            $imagePaths = array_merge($imagePaths, array_reverse($imagePaths));
        }

        $outputGifPath = storage_path('app/temp/output.gif');
        $command = sprintf(
            'convert -delay %d -resize %s %s %s',
            $delay,
            escapeshellarg($targetSize),
            implode(' ', array_map('escapeshellarg', $imagePaths)),
            escapeshellarg($outputGifPath)
        );

        exec($command, $output, $returnVar);

        if ($returnVar !== 0) {
            return response()->json(['error' => 'Failed to create GIF'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        return response()->file($outputGifPath, [
            'Content-Type' => 'image/gif',
            'Content-Disposition' => 'inline; filename="output.gif"',
        ]);
    }
}