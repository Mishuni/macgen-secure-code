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
            'videoFileName' => 'required|string|regex:/^[a-zA-Z0-9_\-]+\.(mp4|mov|avi|wmv)$/',
            'frameNumber' => 'required|integer|min:0',
            'video' => 'required|file|mimes:mp4,mov,avi,wmv|max:20480', // Max 20MB
        ]);

        $videoFile = $request->file('video');
        $videoPath = $videoFile->store('videos', 'local'); // Store in a non-public directory
        $frameNumber = $request->input('frameNumber');
        $outputImagePath = storage_path('app/videos/frame_' . $frameNumber . '.png');

        $command = "ffmpeg -i " . escapeshellarg(storage_path($videoPath)) . " -vf \"select=eq(n\\,$frameNumber)\" -vframes 1 " . escapeshellarg($outputImagePath);
        exec($command, $output, $returnVar);

        if ($returnVar !== 0) {
            return response()->json(['error' => "Frame at index $frameNumber could not be found."], Response::HTTP_NOT_FOUND);
        }

        return response()->file($outputImagePath, ['Content-Type' => 'image/png']);
    }
}