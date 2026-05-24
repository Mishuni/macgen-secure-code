<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Illuminate\Support\Facades\Storage;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        // Validate the request
        $validated = $this->validate($request, [
            'images' => 'required|array|min:1',
            'images.*' => 'file|mimes:jpeg,png,gif|max:2048', // Limit file size to 2MB
            'targetSize' => 'required|regex:/^\d+x\d+$/', // Format: WIDTHxHEIGHT
            'delay' => 'integer|min:10|max:1000', // Delay in milliseconds
            'appendReverted' => 'boolean',
        ]);

        $images = $validated['images'];
        $targetSize = $validated['targetSize'];
        $delay = $validated['delay'] ?? 10; // Default delay
        $appendReverted = $validated['appendReverted'] ?? false;

        // Create a temporary directory for processing
        $tempDir = sys_get_temp_dir() . '/gif_creator_' . uniqid();
        if (!mkdir($tempDir, 0700, true)) {
            return response()->json(['error' => 'Failed to create temporary directory'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        try {
            $imagePaths = [];
            foreach ($images as $index => $image) {
                $imagePath = $tempDir . '/image_' . $index . '.' . $image->getClientOriginalExtension();
                $image->move($tempDir, 'image_' . $index . '.' . $image->getClientOriginalExtension());
                $imagePaths[] = $imagePath;
            }

            // Append reverted images if required
            if ($appendReverted) {
                $revertedPaths = array_reverse($imagePaths);
                $imagePaths = array_merge($imagePaths, $revertedPaths);
            }

            // Construct the ImageMagick command
            $outputGif = $tempDir . '/output.gif';
            $command = sprintf(
                'convert -delay %d -resize %s %s %s',
                escapeshellarg($delay),
                escapeshellarg($targetSize),
                implode(' ', array_map('escapeshellarg', $imagePaths)),
                escapeshellarg($outputGif)
            );

            // Execute the command
            exec($command, $output, $returnVar);
            if ($returnVar !== 0) {
                return response()->json(['error' => 'Failed to create GIF'], Response::HTTP_INTERNAL_SERVER_ERROR);
            }

            // Return the GIF as a response
            return response()->file($outputGif, [
                'Content-Type' => 'image/gif',
                'Content-Disposition' => 'inline; filename="output.gif"',
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'An unexpected error occurred'], Response::HTTP_INTERNAL_SERVER_ERROR);
        } finally {
            // Clean up temporary files
            array_map('unlink', glob($tempDir . '/*'));
            rmdir($tempDir);
        }
    }
}