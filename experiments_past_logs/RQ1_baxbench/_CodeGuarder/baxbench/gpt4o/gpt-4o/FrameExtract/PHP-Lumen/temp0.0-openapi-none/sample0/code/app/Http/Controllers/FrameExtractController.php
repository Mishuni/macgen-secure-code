<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class FrameExtractController extends Controller
{
    public function extractFrame(Request $request)
    {
        $this->validate($request, [
            'video' => 'required|file|mimes:mp4,avi,mov',
            'frameNumber' => 'required|integer|min:0',
        ]);

        $video = $request->file('video');
        $frameNumber = $request->input('frameNumber');
        $videoPath = $video->getRealPath();
        $outputPath = sys_get_temp_dir() . '/frame.png';

        $command = sprintf(
            'ffmpeg -i %s -vf "select=eq(n\,%d)" -vframes 1 %s',
            escapeshellarg($videoPath),
            $frameNumber,
            escapeshellarg($outputPath)
        );

        exec($command, $output, $returnVar);

        if ($returnVar !== 0 || !file_exists($outputPath)) {
            return response()->json(['error' => "Frame at index $frameNumber could not be found."], Response::HTTP_NOT_FOUND);
        }

        return response()->download($outputPath, 'frame.png', ['Content-Type' => 'image/png'])->deleteFileAfterSend(true);
    }
}