<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserProfileController;

Route::post('/add_profile', [UserProfileController::class, 'addProfile']);
Route::get('/profile/{username}', [UserProfileController::class, 'getProfile']);
Route::get('/profile-photo/{username}', [UserProfileController::class, 'getProfilePhoto']);