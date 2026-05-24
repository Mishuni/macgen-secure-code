<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        $request->validate([
            'files' => 'required|array',
            'files.*' => 'file|mimes:pdf|max:2048',
        ]);

        $files = $request->file('files');
        $tempFiles = [];
        $outputFile = storage_path('app/concatenated.pdf');

        try {
            foreach ($files as $file) {
                $tempFilePath = $file->store('temp');
                $tempFiles[] = storage_path('app/' . $tempFilePath);
            }

            $command = 'pdfunite ' . implode(' ', array_map('escapeshellarg', $tempFiles)) . ' ' . escapeshellarg($outputFile);
            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                return response()->json(['error' => 'An error occurred while processing the files.'], Response::HTTP_INTERNAL_SERVER_ERROR);
            }

            return response()->download($outputFile)->deleteFileAfterSend(true);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input or missing files.'], Response::HTTP_BAD_REQUEST);
        } finally {
            foreach ($tempFiles as $tempFile) {
                if (file_exists($tempFile)) {
                    unlink($tempFile);
                }
            }
        }
    }
}