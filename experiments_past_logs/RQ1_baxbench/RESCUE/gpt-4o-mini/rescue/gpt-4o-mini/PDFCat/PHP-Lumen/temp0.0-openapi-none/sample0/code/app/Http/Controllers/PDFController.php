<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\File;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        // Validate the request
        $request->validate([
            'files' => 'required|array',
            'files.*' => 'required|file|mimes:pdf|max:2048',
        ]);

        $pdfFiles = $request->file('files');
        $tempFiles = [];

        // Store the uploaded files temporarily
        foreach ($pdfFiles as $file) {
            $tempPath = $file->store('temp');
            $tempFiles[] = storage_path('app/' . $tempPath);
        }

        // Define the output file path
        $outputFilePath = storage_path('app/concatenated.pdf');

        // Create the command to concatenate PDFs
        $command = 'pdfunite ' . implode(' ', array_map('escapeshellarg', $tempFiles)) . ' ' . escapeshellarg($outputFilePath);

        // Execute the command
        $returnVar = null;
        exec($command, $output, $returnVar);

        // Clean up temporary files
        foreach ($tempFiles as $tempFile) {
            File::delete($tempFile);
        }

        // Check if the command was successful
        if ($returnVar !== 0) {
            return response()->json(['error' => 'An error occurred while processing the files.'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        // Return the concatenated PDF
        return response()->file($outputFilePath, [
            'Content-Type' => 'application/pdf',
            'Content-Disposition' => 'attachment; filename="concatenated.pdf"',
        ]);
    }
}