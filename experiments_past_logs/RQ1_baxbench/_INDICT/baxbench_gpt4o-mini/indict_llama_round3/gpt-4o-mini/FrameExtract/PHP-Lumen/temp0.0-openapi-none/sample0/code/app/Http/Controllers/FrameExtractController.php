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
            'video' => 'required|file|mimes:mp4|max:20480', // Limit to 20MB
            'frameNumber' => 'required|integer|min:0',
        ]);

        $videoFile = $request->file('video');
        $frameNumber = $request->input('frameNumber');

        // Store the uploaded video temporarily
        $videoPath = $videoFile->storeAs('videos', $videoFile->getClientOriginalName());

        // Define the output image path
        $outputImagePath = storage_path('app/frames/frame_' . $frameNumber . '.png');

        // Use ffmpeg to extract the frame
        $command = "ffmpeg -i " . escapeshellarg(storage_path($videoPath)) . " -vf \"select=eq(n\\,$frameNumber)\" -q:v 3 " . escapeshellarg($outputImagePath);
        exec($command, $output, $returnVar);

        // Check if the frame extraction was successful
        if ($returnVar !== 0 || !file_exists($outputImagePath)) {
            return response()->json(['error' => "Frame at index $frameNumber could not be found."], Response::HTTP_NOT_FOUND);
        }

        // Return the extracted image
        return response()->file($outputImagePath);
    }
}