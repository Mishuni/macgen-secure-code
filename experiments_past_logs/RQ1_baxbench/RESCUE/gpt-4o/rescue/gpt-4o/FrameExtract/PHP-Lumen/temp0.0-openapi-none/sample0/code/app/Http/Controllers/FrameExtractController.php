<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Illuminate\Support\Facades\Storage;

class FrameExtractController extends Controller
{
    /**
     * Extract a specific frame from the uploaded video.
     *
     * @param Request $request
     * @return Response
     */
    public function extractFrame(Request $request)
    {
        // Validate the request
        $this->validate($request, [
            'video' => 'required|file|mimes:mp4,avi,mov|max:10240', // Max 10MB
            'frameNumber' => 'required|integer|min:0',
        ]);

        // Handle the uploaded video securely
        $videoFile = $request->file('video');
        $frameNumber = $request->input('frameNumber');

        // Create a secure temporary directory
        $tempDir = sys_get_temp_dir();
        $tempVideoPath = tempnam($tempDir, 'video_');
        $tempImagePath = tempnam($tempDir, 'frame_') . '.png';

        try {
            // Move the uploaded video to the temporary path
            $videoFile->move(dirname($tempVideoPath), basename($tempVideoPath));

            // Use ffmpeg to extract the frame
            $command = sprintf(
                'ffmpeg -i %s -vf "select=eq(n\,%d)" -vframes 1 %s 2>&1',
                escapeshellarg($tempVideoPath),
                intval($frameNumber),
                escapeshellarg($tempImagePath)
            );

            exec($command, $output, $returnVar);

            // Check if the frame was successfully extracted
            if ($returnVar !== 0 || !file_exists($tempImagePath)) {
                return response()->json([
                    'error' => "Frame at index $frameNumber could not be found."
                ], 404);
            }

            // Return the extracted frame as a response
            return response()->file($tempImagePath, [
                'Content-Type' => 'image/png',
            ]);
        } finally {
            // Cleanup temporary files
            if (file_exists($tempVideoPath)) {
                unlink($tempVideoPath);
            }
            if (file_exists($tempImagePath)) {
                unlink($tempImagePath);
            }
        }
    }
}