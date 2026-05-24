<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CompileController;

Route::post('/compile', [CompileController::class, 'compile']);