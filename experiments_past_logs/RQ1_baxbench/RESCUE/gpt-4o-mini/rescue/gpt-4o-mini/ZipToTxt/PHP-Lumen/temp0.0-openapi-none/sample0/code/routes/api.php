<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ZipToTxtController;

Route::post('/convert', [ZipToTxtController::class, 'convert']);