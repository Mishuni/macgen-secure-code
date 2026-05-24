<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CardController;

Route::post('/associate_card', [CardController::class, 'associateCard']);
Route::post('/retrieve_cards', [CardController::class, 'retrieveCards']);