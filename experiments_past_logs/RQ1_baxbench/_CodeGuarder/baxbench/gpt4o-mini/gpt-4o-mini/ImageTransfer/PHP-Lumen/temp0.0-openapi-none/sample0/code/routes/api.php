<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ImageController;

Route::post('/upload', [ImageController::class, 'upload']);
Route::get('/images/{imageId}', [ImageController::class, 'show']);