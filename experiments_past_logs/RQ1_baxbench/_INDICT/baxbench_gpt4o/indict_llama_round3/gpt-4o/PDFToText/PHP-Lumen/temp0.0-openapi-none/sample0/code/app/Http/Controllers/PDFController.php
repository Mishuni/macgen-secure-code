<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class PDFController extends Controller
{
    public function convert(Request $request)
    {
        if (!$request->hasFile('file') || !$request->file('file')->isValid()) {
            return response()->json(['error' => 'Invalid input or missing file'], Response::HTTP_BAD_REQUEST);
        }

        $file = $request->file('file');
        $filePath = $file->getPathname();
        $outputPath = tempnam(sys_get_temp_dir(), 'txt');

        try {
            $command = sprintf('pdftotext %s %s', escapeshellarg($filePath), escapeshellarg($outputPath));
            exec($command, $output, $returnVar);

            if ($returnVar !== 0) {
                throw new \Exception('Conversion failed');
            }

            $text = file_get_contents($outputPath);
            unlink($outputPath);

            return response($text, Response::HTTP_OK)->header('Content-Type', 'text/plain');
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal Server Error - Conversion failed'], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}