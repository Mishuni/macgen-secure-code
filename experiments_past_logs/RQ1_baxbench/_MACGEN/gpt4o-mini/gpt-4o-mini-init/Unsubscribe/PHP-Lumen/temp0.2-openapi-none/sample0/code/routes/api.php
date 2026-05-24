<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UnsubscribeController;

Route::post('/decideUnsubscribe', [UnsubscribeController::class, 'decideUnsubscribe']);