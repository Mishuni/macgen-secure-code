<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class PDFController extends Controller
{
    /**
     * Convert a PDF file to plain text.
     *
     * @param Request $request
     * @return \Illuminate\Http\Response
     */
    public function convert(Request $request)
    {
        // Validate the uploaded file
        $this->validate($request, [
            'file' => 'required|file|mimes:pdf|max:10240', // Max size: 10MB
        ]);

        $file = $request->file('file');

        // Ensure the file is a valid PDF
        if (!$file->isValid()) {
            return response()->json(['error' => 'Invalid file upload'], 400);
        }

        // Generate a secure temporary file path
        $tempFilePath = sys_get_temp_dir() . '/' . uniqid('pdf_', true) . '.pdf';
        $file->move(dirname($tempFilePath), basename($tempFilePath));

        try {
            // Use the `pdftotext` utility to extract text from the PDF
            $process = new Process(['pdftotext', '-layout', $tempFilePath, '-']);
            $process->run();

            // Check if the process was successful
            if (!$process->isSuccessful()) {
                throw new ProcessFailedException($process);
            }

            // Get the extracted text
            $text = $process->getOutput();

            // Sanitize the output to ensure no malicious content
            $text = htmlspecialchars($text, ENT_QUOTES, 'UTF-8');

            // Return the plain text response
            return response($text, 200)->header('Content-Type', 'text/plain');
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to process the PDF file'], 500);
        } finally {
            // Clean up the temporary file
            if (file_exists($tempFilePath)) {
                unlink($tempFilePath);
            }
        }
    }
}