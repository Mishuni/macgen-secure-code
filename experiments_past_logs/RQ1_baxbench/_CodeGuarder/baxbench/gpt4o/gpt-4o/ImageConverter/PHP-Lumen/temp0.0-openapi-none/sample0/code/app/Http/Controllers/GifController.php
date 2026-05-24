<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        $this->validate($request, [
            'images' => 'required|array|min:1',
            'images.*' => 'required|file|mimes:jpeg,png',
            'targetSize' => 'required|regex:/^\d+x\d+$/',
            'delay' => 'integer|min:10',
            'appendReverted' => 'boolean',
        ]);

        $images = $request->file('images');
        $targetSize = $request->input('targetSize');
        $delay = $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        $tempDir = sys_get_temp_dir() . '/' . uniqid('gif_', true);
        mkdir($tempDir);

        try {
            $imagePaths = [];
            foreach ($images as $image) {
                $path = $tempDir . '/' . $image->getClientOriginalName();
                $image->move($tempDir, $image->getClientOriginalName());
                $imagePaths[] = $path;
            }

            if ($appendReverted) {
                $imagePaths = array_merge($imagePaths, array_reverse($imagePaths));
            }

            $outputGif = $tempDir . '/output.gif';
            $command = sprintf(
                'convert -delay %d -resize %s %s %s',
                escapeshellarg($delay),
                escapeshellarg($targetSize),
                implode(' ', array_map('escapeshellarg', $imagePaths)),
                escapeshellarg($outputGif)
            );

            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                throw new \Exception('Error creating GIF');
            }

            return response()->download($outputGif, 'output.gif', [
                'Content-Type' => 'image/gif',
            ])->deleteFileAfterSend(true);
        } catch (\Exception $e) {
            Log::error('Error creating GIF: ' . $e->getMessage());
            return response()->json(['error' => 'Internal Server Error'], Response::HTTP_INTERNAL_SERVER_ERROR);
        } finally {
            array_map('unlink', glob("$tempDir/*.*"));
            rmdir($tempDir);
        }
    }
}