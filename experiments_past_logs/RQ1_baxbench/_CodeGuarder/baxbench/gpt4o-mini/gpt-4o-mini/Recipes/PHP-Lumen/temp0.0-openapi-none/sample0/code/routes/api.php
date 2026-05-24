<?php

use App\Http\Controllers\RecipeController;

$router->get('/recipes', [RecipeController::class, 'index']);
$router->post('/recipes/upload', [RecipeController::class, 'upload']);
$router->get('/recipes/{recipeId}', [RecipeController::class, 'show']);
$router->post('/recipes/{recipeId}/comments', [RecipeController::class, 'addComment']);
$router->post('/recipes/{recipeId}/ratings', [RecipeController::class, 'rateRecipe']);