<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Symfony\Component\HttpFoundation\Response;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        // Validate the input
        $validator = Validator::make($request->all(), [
            'images' => 'required|array',
            'images.*' => 'required|file|mimes:jpeg,png,gif,jpg',
            'targetSize' => 'required|string|regex:/^\d+x\d+$/',
            'delay' => 'integer|min:0',
            'appendReverted' => 'boolean',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], Response::HTTP_BAD_REQUEST);
        }

        // Extract validated data
        $images = $request->file('images');
        $targetSize = $request->input('targetSize');
        $delay = $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        // Create a temporary directory for the images
        $tempDir = sys_get_temp_dir() . '/gif_creator_' . uniqid();
        mkdir($tempDir);

        // Store images in the temporary directory
        $imagePaths = [];
        foreach ($images as $image) {
            $imagePath = $tempDir . '/' . uniqid() . '.' . $image->getClientOriginalExtension();
            $image->move($tempDir, $imagePath);
            $imagePaths[] = $imagePath;
        }

        // Prepare the command for ImageMagick
        $outputGif = $tempDir . '/output.gif';
        $command = "convert -delay $delay " . implode(' ', $imagePaths) . " $outputGif";

        // Execute the command
        exec($command);

        // Append reverted images if requested
        if ($appendReverted) {
            $revertedImages = array_reverse($imagePaths);
            $command .= " -delay $delay " . implode(' ', $revertedImages) . " $outputGif";
            exec($command);
        }

        // Return the GIF as a response
        return response()->file($outputGif)->deleteFileAfterSend(true);
    }
}