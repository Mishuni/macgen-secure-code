<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class PdfController extends Controller
{
    public function convert(Request $request)
    {
        // Validate the request
        $request->validate([
            'file' => 'required|file|mimes:pdf|max:2048',
        ]);

        // Store the uploaded file temporarily
        $file = $request->file('file');
        $filePath = $file->storeAs('uploads', uniqid() . '.pdf');

        // Convert PDF to text using pdftotext
        $outputFilePath = storage_path('app/uploads/' . uniqid() . '.txt');
        $command = "pdftotext " . escapeshellarg(storage_path('app/' . $filePath)) . " " . escapeshellarg($outputFilePath);
        exec($command, $output, $returnVar);

        // Check for conversion errors
        if ($returnVar !== 0) {
            return response()->json(['error' => 'Conversion failed'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        // Read the converted text
        $textContent = file_get_contents($outputFilePath);

        // Clean up temporary files
        Storage::delete($filePath);
        Storage::delete('uploads/' . basename($outputFilePath));

        return response($textContent, Response::HTTP_OK)
            ->header('Content-Type', 'text/plain');
    }
}