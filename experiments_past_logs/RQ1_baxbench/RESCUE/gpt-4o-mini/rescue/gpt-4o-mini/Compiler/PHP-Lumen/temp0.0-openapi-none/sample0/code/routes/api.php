<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CompilerController;

Route::post('/compile', [CompilerController::class, 'compile']);