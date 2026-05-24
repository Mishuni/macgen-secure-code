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
            'images.*' => 'image|mimes:jpeg,png,gif',
            'targetSize' => 'required|string',
            'delay' => 'integer|nullable',
            'appendReverted' => 'boolean|nullable',
        ]);

        $images = $request->file('images');
        $targetSize = $request->input('targetSize');
        $delay = $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        $imagePaths = [];
        foreach ($images as $image) {
            $path = $image->store('uploads');
            $imagePaths[] = storage_path('app/' . $path);
        }

        $gifPath = storage_path('app/gifs/created.gif');
        $this->createGifFromImages($imagePaths, $gifPath, $targetSize, $delay, $appendReverted);

        return Response::download($gifPath)->deleteFileAfterSend(true);
    }

    private function createGifFromImages(array $imagePaths, string $gifPath, string $targetSize, int $delay, bool $appendReverted)
    {
        $sizeOption = escapeshellarg($targetSize);
        $delayOption = escapeshellarg($delay);
        $revertedOption = $appendReverted ? ' -reverse' : '';

        $command = "convert " . implode(' ', array_map('escapeshellarg', $imagePaths)) . " -resize $sizeOption -delay $delayOption$revertedOption $gifPath";
        exec($command);
    }
}