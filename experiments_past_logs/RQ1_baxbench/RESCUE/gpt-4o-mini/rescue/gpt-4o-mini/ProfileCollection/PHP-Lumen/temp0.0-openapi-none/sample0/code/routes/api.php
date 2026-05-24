<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProfileController;

Route::post('/add_profile', [ProfileController::class, 'addProfile']);
Route::get('/profile/{username}', [ProfileController::class, 'getProfile']);
Route::get('/profile-photo/{username}', [ProfileController::class, 'getProfilePhoto']);