<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\EntryController;

Route::get('/entries', [EntryController::class, 'index']);
Route::post('/entries', [EntryController::class, 'store']);
Route::get('/entries/{entryId}', [EntryController::class, 'show']);
Route::put('/entries/{entryId}', [EntryController::class, 'update']);
Route::get('/entries/{entryId}/edits', [EntryController::class, 'edits']);