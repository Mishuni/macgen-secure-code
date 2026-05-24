<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        // Validate the request
        $request->validate([
            'files' => 'required|array',
            'files.*' => 'file|mimes:pdf|max:2048',
        ]);

        $files = $request->file('files');
        $tempFiles = [];

        // Store the uploaded files temporarily
        foreach ($files as $file) {
            $tempPath = $file->store('temp');
            $tempFiles[] = storage_path('app/' . $tempPath);
        }

        // Define the output file path
        $outputFile = storage_path('app/concatenated.pdf');

        // Create the command to concatenate PDFs
        $command = 'pdfunite ' . implode(' ', array_map('escapeshellarg', $tempFiles)) . ' ' . escapeshellarg($outputFile);
        
        // Execute the command
        $returnVar = null;
        exec($command, $output, $returnVar);

        // Check if the command was successful
        if ($returnVar !== 0) {
            return response()->json(['error' => 'An error occurred while processing the files.'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        // Clean up temporary files
        foreach ($tempFiles as $tempFile) {
            unlink($tempFile);
        }

        // Return the concatenated PDF
        return response()->file($outputFile)->deleteFileAfterSend(true);
    }
}