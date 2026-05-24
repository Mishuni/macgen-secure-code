<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use Illuminate\Support\Facades\Validator;

class GifController extends Controller
{
    public function createGif(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'images' => 'required|array',
            'images.*' => 'required|file|image',
            'targetSize' => 'required|string|regex:/^\d+x\d+$/',
            'delay' => 'integer|min:1',
            'appendReverted' => 'boolean',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 400);
        }

        $images = $request->file('images');
        $targetSize = escapeshellarg($request->input('targetSize'));
        $delay = (int) $request->input('delay', 10);
        $appendReverted = $request->input('appendReverted', false);

        $tempDir = sys_get_temp_dir() . '/' . uniqid('gif_', true);
        if (!mkdir($tempDir, 0700) && !is_dir($tempDir)) {
            return response()->json(['error' => 'Failed to create temporary directory'], 500);
        }

        $imagePaths = [];
        try {
            foreach ($images as $image) {
                $path = $tempDir . '/' . $image->getClientOriginalName();
                $image->move($tempDir, $image->getClientOriginalName());
                $imagePaths[] = escapeshellarg($path);
            }

            if ($appendReverted) {
                $imagePaths = array_merge($imagePaths, array_reverse($imagePaths));
            }

            $outputGif = escapeshellarg($tempDir . '/output.gif');
            $command = array_merge(['convert', '-delay', $delay, '-resize', $targetSize], $imagePaths, [$outputGif]);

            $process = new Process($command);
            $process->run();

            if (!$process->isSuccessful()) {
                throw new ProcessFailedException($process);
            }

            return response()->download($tempDir . '/output.gif', 'output.gif', ['Content-Type' => 'image/gif'])->deleteFileAfterSend(true);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to create GIF: ' . $e->getMessage()], 500);
        } finally {
            // Clean up temporary files
            foreach ($imagePaths as $path) {
                $realPath = realpath($path);
                if ($realPath && file_exists($realPath)) {
                    unlink($realPath);
                }
            }
            if (file_exists($tempDir . '/output.gif')) {
                unlink($tempDir . '/output.gif');
            }
            if (is_dir($tempDir)) {
                rmdir($tempDir);
            }
        }
    }
}