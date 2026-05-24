<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Symfony\Component\HttpFoundation\File\Exception\FileException;

class PDFController extends Controller
{
    public function convert(Request $request)
    {
        // Validate the request
        $request->validate([
            'file' => 'required|file|mimes:pdf|max:2048', // Limit to PDF files and size
        ]);

        try {
            // Store the uploaded file temporarily
            $file = $request->file('file');
            $path = $file->storeAs('uploads', 'temp.pdf');

            // Use pdftotext to convert PDF to text
            $output = [];
            $returnVar = 0;
            exec("pdftotext " . escapeshellarg(storage_path('app/' . $path)) . " -", $output, $returnVar);

            // Check if the conversion was successful
            if ($returnVar !== 0) {
                return response()->json(['error' => 'Conversion failed'], Response::HTTP_INTERNAL_SERVER_ERROR);
            }

            // Return the converted text
            return response()->json(implode("\n", $output), Response::HTTP_OK);
        } catch (FileException $e) {
            return response()->json(['error' => 'Invalid file upload'], Response::HTTP_BAD_REQUEST);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal Server Error'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}