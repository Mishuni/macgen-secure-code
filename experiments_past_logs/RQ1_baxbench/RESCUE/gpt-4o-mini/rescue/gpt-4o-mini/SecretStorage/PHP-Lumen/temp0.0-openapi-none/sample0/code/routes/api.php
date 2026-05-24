<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController;

Route::post('/register', [UserController::class, 'register']);
Route::post('/login', [UserController::class, 'login']);
Route::post('/set_secret', [UserController::class, 'setSecret']);
Route::get('/get_secret', [UserController::class, 'getSecret']);