<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\File\Exception\FileException;
use Symfony\Component\HttpFoundation\File\UploadedFile;
use Illuminate\Support\Facades\Storage;

class PDFController extends Controller
{
    public function convert(Request $request)
    {
        $this->validate($request, [
            'file' => 'required|file|mimes:pdf|max:10240', // max 10MB
        ]);

        /** @var UploadedFile $file */
        $file = $request->file('file');

        try {
            $filePath = $file->storeAs('uploads', uniqid() . '.pdf', 'local');
            $outputPath = storage_path('app/uploads/' . uniqid() . '.txt');

            $command = escapeshellcmd("pdftotext " . escapeshellarg(storage_path('app/' . $filePath)) . " " . escapeshellarg($outputPath));
            $output = shell_exec($command);

            if (!file_exists($outputPath)) {
                return response()->json(['error' => 'Conversion failed'], 500);
            }

            $text = file_get_contents($outputPath);
            unlink(storage_path('app/' . $filePath));
            unlink($outputPath);

            return response($text, 200)->header('Content-Type', 'text/plain');
        } catch (FileException $e) {
            return response()->json(['error' => 'File upload failed'], 400);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal Server Error'], 500);
        }
    }
}