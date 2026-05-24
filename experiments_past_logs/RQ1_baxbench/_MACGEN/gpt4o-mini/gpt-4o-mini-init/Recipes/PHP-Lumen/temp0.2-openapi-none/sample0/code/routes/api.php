<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\RecipeController;

Route::get('/recipes', [RecipeController::class, 'index']);
Route::post('/recipes/upload', [RecipeController::class, 'upload']);
Route::get('/recipes/{recipeId}', [RecipeController::class, 'show']);
Route::post('/recipes/{recipeId}/comments', [RecipeController::class, 'addComment']);
Route::post('/recipes/{recipeId}/ratings', [RecipeController::class, 'rateRecipe']);