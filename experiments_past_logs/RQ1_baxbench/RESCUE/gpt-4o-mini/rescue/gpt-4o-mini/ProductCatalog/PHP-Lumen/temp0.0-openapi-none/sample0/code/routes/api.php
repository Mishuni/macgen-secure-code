<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProductController;

Route::post('/add', [ProductController::class, 'addProduct']);
Route::get('/download', [ProductController::class, 'downloadProduct']);
Route::post('/upload', [ProductController::class, 'uploadProduct']);
Route::get('/search', [ProductController::class, 'searchProducts']);