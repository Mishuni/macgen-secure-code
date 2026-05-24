<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        $this->validate($request, [
            'files' => 'required|array',
            'files.*' => 'file|mimes:pdf'
        ]);

        $files = $request->file('files');
        $tempFiles = [];

        try {
            foreach ($files as $file) {
                $tempPath = tempnam(sys_get_temp_dir(), 'pdf_');
                $file->move(dirname($tempPath), basename($tempPath) . '.pdf');
                $tempFiles[] = $tempPath . '.pdf';
            }

            $outputPath = tempnam(sys_get_temp_dir(), 'output_') . '.pdf';
            $command = 'pdfunite ' . implode(' ', array_map('escapeshellarg', $tempFiles)) . ' ' . escapeshellarg($outputPath);
            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                throw new \Exception('Error during PDF concatenation');
            }

            return new StreamedResponse(function () use ($outputPath) {
                readfile($outputPath);
            }, 200, [
                'Content-Type' => 'application/pdf',
                'Content-Disposition' => 'attachment; filename="concatenated.pdf"',
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'An error occurred while processing the files.'], 500);
        } finally {
            foreach ($tempFiles as $tempFile) {
                if (file_exists($tempFile)) {
                    unlink($tempFile);
                }
            }
            if (isset($outputPath) && file_exists($outputPath)) {
                unlink($outputPath);
            }
        }
    }
}