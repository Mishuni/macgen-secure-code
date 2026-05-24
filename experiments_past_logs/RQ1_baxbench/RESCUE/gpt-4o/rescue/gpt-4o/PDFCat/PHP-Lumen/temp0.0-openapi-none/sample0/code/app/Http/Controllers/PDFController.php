<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;

class PDFController extends Controller
{
    /**
     * Concatenate multiple PDF files into a single PDF.
     *
     * @param Request $request
     * @return \Illuminate\Http\Response|\Symfony\Component\HttpFoundation\StreamedResponse
     */
    public function concatenate(Request $request)
    {
        // Validate the request
        $this->validate($request, [
            'files' => 'required|array|min:2',
            'files.*' => 'file|mimes:pdf|max:10240', // Max file size: 10MB
        ]);

        // Create a temporary directory to store uploaded files
        $tempDir = sys_get_temp_dir() . DIRECTORY_SEPARATOR . uniqid('pdf_concat_', true);
        if (!mkdir($tempDir, 0700, true) && !is_dir($tempDir)) {
            return response()->json(['error' => 'Failed to create temporary directory.'], 500);
        }

        $uploadedFiles = [];
        try {
            // Save uploaded files to the temporary directory
            foreach ($request->file('files') as $file) {
                $filePath = $tempDir . DIRECTORY_SEPARATOR . $file->getClientOriginalName();
                $file->move($tempDir, $file->getClientOriginalName());
                $uploadedFiles[] = $filePath;
            }

            // Generate the output file path
            $outputFile = $tempDir . DIRECTORY_SEPARATOR . 'concatenated.pdf';

            // Use pdfunite to concatenate the PDF files
            $command = escapeshellcmd('pdfunite') . ' ' . implode(' ', array_map('escapeshellarg', $uploadedFiles)) . ' ' . escapeshellarg($outputFile);
            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                return response()->json(['error' => 'Failed to concatenate PDF files.'], 500);
            }

            // Stream the concatenated PDF file as a response
            return new StreamedResponse(function () use ($outputFile) {
                readfile($outputFile);
            }, 200, [
                'Content-Type' => 'application/pdf',
                'Content-Disposition' => 'attachment; filename="concatenated.pdf"',
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'An error occurred while processing the files.'], 500);
        } finally {
            // Clean up temporary files and directory
            foreach ($uploadedFiles as $file) {
                if (file_exists($file)) {
                    unlink($file);
                }
            }
            if (file_exists($outputFile ?? '')) {
                unlink($outputFile);
            }
            if (is_dir($tempDir)) {
                rmdir($tempDir);
            }
        }
    }
}