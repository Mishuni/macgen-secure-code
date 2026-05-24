<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PDFController;

Route::post('/concatenate', [PDFController::class, 'concatenate']);