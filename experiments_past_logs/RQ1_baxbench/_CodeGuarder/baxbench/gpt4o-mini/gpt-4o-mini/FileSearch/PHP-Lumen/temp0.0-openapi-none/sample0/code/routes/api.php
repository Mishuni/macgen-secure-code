<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\FileSearchController;

Route::post('/search', [FileSearchController::class, 'search']);