<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/recommender', 'RecommendationController@getRecommendations');
$router->post('/recommender', 'RecommendationController@postProduct');