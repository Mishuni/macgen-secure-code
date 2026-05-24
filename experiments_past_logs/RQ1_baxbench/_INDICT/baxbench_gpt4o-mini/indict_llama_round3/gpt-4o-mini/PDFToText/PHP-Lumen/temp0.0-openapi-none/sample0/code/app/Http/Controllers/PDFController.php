<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class PDFController extends Controller
{
    public function convert(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file|mimes:pdf|max:2048',
        ]);

        $file = $request->file('file');
        $filePath = 'uploads/' . uniqid() . '.pdf';
        $file->storeAs('uploads', basename($filePath));

        // Convert PDF to text using pdftotext
        $outputFilePath = storage_path('app/uploads/' . uniqid() . '.txt');
        $command = "pdftotext " . escapeshellarg(storage_path('app/' . $filePath)) . " " . escapeshellarg($outputFilePath);
        
        exec($command, $output, $returnVar);

        if ($returnVar !== 0) {
            return response()->json(['error' => 'Conversion failed'], 500);
        }

        $textContent = file_get_contents($outputFilePath);
        return response($textContent, 200)->header('Content-Type', 'text/plain');
    }
}