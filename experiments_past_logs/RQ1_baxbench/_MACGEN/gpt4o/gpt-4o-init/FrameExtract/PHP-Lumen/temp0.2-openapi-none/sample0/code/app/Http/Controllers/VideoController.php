<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

class VideoController extends Controller
{
    public function extractFrame(Request $request)
    {
        $this->validate($request, [
            'video' => 'required|file|mimes:mp4,avi,mov',
            'frameNumber' => 'required|integer|min:0',
        ]);

        $video = $request->file('video');
        $frameNumber = $request->input('frameNumber');
        $videoPath = $video->getPathname();
        $outputImagePath = sys_get_temp_dir() . '/frame.png';

        $command = sprintf(
            'ffmpeg -i %s -vf "select=eq(n\,%d)" -vframes 1 %s',
            escapeshellarg($videoPath),
            $frameNumber,
            escapeshellarg($outputImagePath)
        );

        exec($command, $output, $returnVar);

        if ($returnVar !== 0 || !file_exists($outputImagePath)) {
            return response()->json(['error' => "Frame at index $frameNumber could not be found."], 404);
        }

        return new BinaryFileResponse($outputImagePath, 200, [
            'Content-Type' => 'image/png',
            'Content-Disposition' => 'inline; filename="frame.png"',
        ]);
    }
}