<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController;

Route::post('/invite_user', [UserController::class, 'inviteUser']);
Route::post('/create_user', [UserController::class, 'createUser']);