<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class FrameExtractController extends Controller
{
    public function extractFrame(Request $request)
    {
        $request->validate([
            'videoFileName' => 'required|string|max:255',
            'frameNumber' => 'required|integer|min:0',
            'video' => 'required|file|mimes:mp4,mov,avi,wmv|max:10240', // 10MB max
        ]);

        $videoFile = $request->file('video');
        $frameNumber = $request->input('frameNumber');
        $videoFileName = $request->input('videoFileName');

        // Store the uploaded video temporarily
        $tempPath = $videoFile->storeAs('videos', $videoFileName);

        // Define the output image path
        $outputImagePath = storage_path('app/images/frame_' . $frameNumber . '.png');

        // Use ffmpeg to extract the frame
        $command = sprintf('ffmpeg -i %s -vf "select=eq(n\,%d)" -q:v 2 %s', escapeshellarg(storage_path($tempPath)), $frameNumber, escapeshellarg($outputImagePath));
        exec($command, $output, $returnVar);

        // Check if the frame extraction was successful
        if ($returnVar !== 0) {
            return response()->json(['error' => "Frame at index $frameNumber could not be found."], Response::HTTP_NOT_FOUND);
        }

        // Return the extracted frame
        return response()->file($outputImagePath);
    }
}