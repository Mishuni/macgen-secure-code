<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\FrameExtractController;

Route::post('/extract', [FrameExtractController::class, 'extractFrame']);