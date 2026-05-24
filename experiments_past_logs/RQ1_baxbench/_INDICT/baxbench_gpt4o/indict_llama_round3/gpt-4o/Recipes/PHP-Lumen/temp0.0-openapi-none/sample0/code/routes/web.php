<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/recipes', 'RecipeController@getRecipes');
$router->post('/recipes/upload', 'RecipeController@uploadRecipe');
$router->get('/recipes/{recipeId}', 'RecipeController@getRecipe');
$router->post('/recipes/{recipeId}/comments', 'RecipeController@addComment');
$router->post('/recipes/{recipeId}/ratings', 'RecipeController@rateRecipe');