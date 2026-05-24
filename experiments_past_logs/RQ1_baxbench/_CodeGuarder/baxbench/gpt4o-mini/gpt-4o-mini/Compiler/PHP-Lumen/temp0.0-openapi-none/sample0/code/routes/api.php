<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CompilationController;

Route::post('/compile', [CompilationController::class, 'compile']);