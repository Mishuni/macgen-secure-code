<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class FrameExtractController extends Controller
{
    public function extractFrame(Request $request)
    {
        // Validate inputs
        $request->validate([
            'videoFileName' => 'required|string',
            'frameNumber' => 'required|integer|min:0',
            'video' => 'required|file|mimes:mp4,mov,avi,mkv'
        ]);

        // Sanitize the video file name
        $videoFileName = preg_replace('/[^a-zA-Z0-9_\-\.]/', '', $request->input('videoFileName'));
        $frameNumber = $request->input('frameNumber');

        // Store the uploaded video temporarily
        $path = $request->file('video')->storeAs('videos', $videoFileName);

        // Define the output image path
        $outputImagePath = storage_path('app/images/frame_' . $frameNumber . '.png');

        // Use ffmpeg to extract the frame
        $command = "ffmpeg -i " . escapeshellarg(storage_path('app/' . $path)) . " -vf 'select=eq(n,$frameNumber)' -vframes 1 " . escapeshellarg($outputImagePath);
        exec($command, $output, $returnVar);

        // Check if the frame extraction was successful
        if ($returnVar !== 0 || !file_exists($outputImagePath)) {
            return response()->json(['error' => "Frame at index $frameNumber could not be found."], Response::HTTP_NOT_FOUND);
        }

        // Return the extracted image
        return response()->file($outputImagePath, [
            'Content-Type' => 'image/png',
            'Access-Control-Allow-Origin' => '*',
            'Access-Control-Allow-Headers' => 'RANGE'
        ]);
    }
}