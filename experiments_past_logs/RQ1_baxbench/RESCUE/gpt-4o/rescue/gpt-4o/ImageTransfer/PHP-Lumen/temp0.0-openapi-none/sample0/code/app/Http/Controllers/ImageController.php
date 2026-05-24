<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class ImageController extends Controller
{
    private $storagePath = __DIR__ . '/../../../storage/app/images';

    public function __construct()
    {
        // Ensure the storage directory exists
        if (!is_dir($this->storagePath)) {
            mkdir($this->storagePath, 0755, true);
        }
    }

    /**
     * Handle image upload and return a shareable link.
     */
    public function upload(Request $request)
    {
        try {
            // Validate the request
            $this->validate($request, [
                'file' => 'required|file|mimes:jpeg,png,gif,bmp,webp|max:5120', // Max 5MB
            ]);

            $file = $request->file('file');

            // Generate a unique ID for the image
            $imageId = Str::uuid()->toString();

            // Sanitize the file name and store the file
            $extension = $file->getClientOriginalExtension();
            $filename = $imageId . '.' . $extension;
            $file->move($this->storagePath, $filename);

            // Return the shareable link
            return response()->json([
                'id' => $imageId,
            ], 200);
        } catch (\Illuminate\Validation\ValidationException $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }

    /**
     * Serve the image for viewing in the browser.
     */
    public function view($imageId)
    {
        try {
            // Sanitize the image ID
            $imageId = basename($imageId);

            // Find the image file
            $files = glob($this->storagePath . '/' . $imageId . '.*');
            if (empty($files)) {
                return response()->json(['error' => 'Image not found'], 404);
            }

            $filePath = $files[0];
            $mimeType = mime_content_type($filePath);

            // Serve the image
            return response()->file($filePath, [
                'Content-Type' => $mimeType,
                'Content-Disposition' => 'inline', // Ensure the image is viewable in the browser
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error'], 500);
        }
    }
}