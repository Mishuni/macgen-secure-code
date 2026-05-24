<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class PDFController extends Controller
{
    public function concatenate(Request $request)
    {
        $this->validate($request, [
            'files' => 'required|array',
            'files.*' => 'file|mimes:pdf|max:2048',
        ]);

        $filePaths = [];
        foreach ($request->file('files') as $file) {
            $path = $file->store('pdfs');
            $filePaths[] = storage_path('app/' . $path);
        }

        $outputFilePath = storage_path('app/pdfs/concatenated.pdf');
        $command = 'pdfunite ' . implode(' ', array_map('escapeshellarg', $filePaths)) . ' ' . escapeshellarg($outputFilePath);

        exec($command, $output, $returnVar);

        if ($returnVar !== 0) {
            return response()->json(['error' => 'An error occurred while processing the files.'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }

        return response()->download($outputFilePath)->deleteFileAfterSend(true);
    }
}