<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Illuminate\Support\Str;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        $this->validate($request, [
            'files' => 'required|array',
            'files.*' => 'file|mimes:pdf'
        ]);

        $files = $request->file('files');
        $tempDir = sys_get_temp_dir();
        $inputFiles = [];

        try {
            foreach ($files as $file) {
                $uniqueName = Str::uuid() . '.pdf';
                $filePath = $tempDir . '/' . $uniqueName;
                $file->move($tempDir, $uniqueName);
                $inputFiles[] = escapeshellarg($filePath);
            }

            $outputFile = $tempDir . '/' . Str::uuid() . '_concatenated.pdf';
            $command = 'pdfunite ' . implode(' ', $inputFiles) . ' ' . escapeshellarg($outputFile);
            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                return response()->json(['error' => 'An error occurred while processing the files.'], 500);
            }

            return new StreamedResponse(function () use ($outputFile) {
                readfile($outputFile);
            }, 200, [
                'Content-Type' => 'application/pdf',
                'Content-Disposition' => 'attachment; filename="concatenated.pdf"',
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'An error occurred while processing the files.'], 500);
        } finally {
            foreach ($inputFiles as $file) {
                $file = str_replace("'", "", $file); // Remove quotes added by escapeshellarg
                if (file_exists($file)) {
                    unlink($file);
                }
            }
            if (isset($outputFile) && file_exists($outputFile)) {
                unlink($outputFile);
            }
        }
    }
}