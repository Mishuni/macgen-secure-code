<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\LogController;

Route::post('/log', [LogController::class, 'logMessage']);
Route::get('/logs', [LogController::class, 'getLogs']);