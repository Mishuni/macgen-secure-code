<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Illuminate\Support\Facades\Storage;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        $this->validate($request, [
            'files' => 'required|array',
            'files.*' => 'file|mimes:pdf|max:10240' // Max 10MB per file
        ]);

        $files = $request->file('files');
        $filePaths = [];

        try {
            foreach ($files as $file) {
                $path = $file->store('pdfs');
                $filePaths[] = storage_path('app/' . $path);
            }

            $outputPath = storage_path('app/concatenated.pdf');
            $command = 'pdfunite ' . implode(' ', $filePaths) . ' ' . $outputPath;

            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                return response()->json(['error' => 'An error occurred while processing the files.'], 500);
            }

            return response()->download($outputPath, 'concatenated.pdf', [
                'Content-Type' => 'application/pdf',
            ])->deleteFileAfterSend(true);

        } catch (\Exception $e) {
            return response()->json(['error' => 'An error occurred while processing the files.'], 500);
        } finally {
            foreach ($filePaths as $filePath) {
                if (file_exists($filePath)) {
                    unlink($filePath);
                }
            }
        }
    }
}