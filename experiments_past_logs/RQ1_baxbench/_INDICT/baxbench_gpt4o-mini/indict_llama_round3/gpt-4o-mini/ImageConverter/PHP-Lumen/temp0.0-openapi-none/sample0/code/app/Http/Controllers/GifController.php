<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        $request->validate([
            'images' => 'required|array',
            'targetSize' => 'required|string',
            'delay' => 'integer|nullable',
            'appendReverted' => 'boolean|nullable',
        ]);

        $images = $request->file('images');
        $targetSize = escapeshellarg($request->input('targetSize'));
        $delay = $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        $imagePaths = [];
        foreach ($images as $image) {
            // Validate the file type
            if (!in_array($image->getClientOriginalExtension(), ['jpg', 'jpeg', 'png', 'gif'])) {
                return response()->json(['error' => 'Invalid image type. Only JPG, PNG, and GIF are allowed.'], Response::HTTP_BAD_REQUEST);
            }
            $imagePaths[] = escapeshellarg($image->getPathname());
        }

        // Create a unique output filename
        $outputGif = tempnam(sys_get_temp_dir(), 'gif_') . '.gif';

        // Create the GIF command
        $gifCommand = 'convert -delay ' . (int)$delay . ' -resize ' . $targetSize . ' ' . implode(' ', $imagePaths) . ' ' . escapeshellarg($outputGif);

        if ($appendReverted) {
            $gifCommand .= ' && convert -delay ' . (int)$delay . ' -resize ' . $targetSize . ' ' . implode(' ', array_reverse($imagePaths)) . ' ' . escapeshellarg($outputGif) . ' -append ' . escapeshellarg($outputGif);
        }

        // Execute the command
        exec($gifCommand, $output, $returnVar);

        if ($returnVar !== 0) {
            return response()->json(['error' => 'Failed to create GIF.'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        // Return the GIF file
        return response()->file($outputGif, [
            'Content-Type' => 'image/gif',
            'Content-Disposition' => 'attachment; filename="output.gif"',
        ]);
    }
}