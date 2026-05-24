<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\MerchantController;

Route::post('/merchants/register', [MerchantController::class, 'register']);
Route::post('/merchants/login', [MerchantController::class, 'login']);
Route::post('/merchants/upload-wares', [MerchantController::class, 'uploadWares'])->middleware('auth');
Route::get('/wares', [MerchantController::class, 'getWares'])->middleware('auth');