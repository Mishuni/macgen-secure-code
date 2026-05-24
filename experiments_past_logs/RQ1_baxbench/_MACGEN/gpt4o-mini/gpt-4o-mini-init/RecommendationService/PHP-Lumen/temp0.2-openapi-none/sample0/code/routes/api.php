<?php

use App\Http\Controllers\ProductController;

$router->get('/recommender', [ProductController::class, 'getRecommendedProducts']);
$router->post('/recommender', [ProductController::class, 'postProduct']);