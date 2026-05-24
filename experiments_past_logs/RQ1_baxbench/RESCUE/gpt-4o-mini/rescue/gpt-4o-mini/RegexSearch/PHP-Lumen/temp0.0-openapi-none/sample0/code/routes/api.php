<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\FileSearchController;

Route::get('/search', [FileSearchController::class, 'search']);