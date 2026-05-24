<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\SongController;

Route::post('/download', [SongController::class, 'streamSong']);