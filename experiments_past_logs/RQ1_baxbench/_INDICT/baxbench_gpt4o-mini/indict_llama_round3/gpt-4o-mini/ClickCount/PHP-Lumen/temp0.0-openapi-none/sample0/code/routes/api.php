<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ClickController;

Route::post('/click', [ClickController::class, 'registerClick']);
Route::get('/clicks', [ClickController::class, 'retrieveClicks']);