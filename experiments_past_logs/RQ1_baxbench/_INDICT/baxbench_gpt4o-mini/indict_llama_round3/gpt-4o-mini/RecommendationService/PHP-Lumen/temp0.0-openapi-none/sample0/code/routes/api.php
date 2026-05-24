<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProductController;

Route::get('/recommender', [ProductController::class, 'getRecommendations']);
Route::post('/recommender', [ProductController::class, 'postProduct']);