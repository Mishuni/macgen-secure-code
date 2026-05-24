<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\GifController;

Route::post('/create-gif', [GifController::class, 'createGif']);