<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class PdfController extends Controller
{
    public function convert(Request $request)
    {
        // Validate the uploaded file
        $request->validate([
            'file' => 'required|file|mimes:pdf|max:2048',
        ]);

        // Store the uploaded PDF file securely
        $file = $request->file('file');
        $filePath = $file->storeAs('uploads', uniqid() . '.pdf');

        // Prepare to execute the pdftotext command
        $output = [];
        $returnVar = 0;
        exec("pdftotext " . escapeshellarg(storage_path('app/' . $filePath)) . " -", $output, $returnVar);

        // Check for conversion errors
        if ($returnVar !== 0) {
            return response()->json(['error' => 'Conversion failed'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        // Return the converted text
        return response(implode("\n", $output), Response::HTTP_OK)
            ->header('Content-Type', 'text/plain');
    }
}