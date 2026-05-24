<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProcessController;

Route::post('/monitor/commands', [ProcessController::class, 'monitorCommands']);