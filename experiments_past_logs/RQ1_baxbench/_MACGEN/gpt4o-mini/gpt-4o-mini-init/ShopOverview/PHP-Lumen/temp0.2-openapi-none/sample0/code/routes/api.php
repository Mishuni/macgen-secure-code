<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\MerchantController;
use App\Http\Controllers\WareController;

Route::post('/merchants/register', [MerchantController::class, 'register']);
Route::post('/merchants/login', [MerchantController::class, 'login']);
Route::post('/merchants/upload-wares', [WareController::class, 'upload']);
Route::get('/wares', [WareController::class, 'index']);