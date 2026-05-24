<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PdfController;

Route::post('/convert', [PdfController::class, 'convert']);