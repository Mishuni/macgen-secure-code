<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ZipController;

Route::post('/convert', [ZipController::class, 'convert']);