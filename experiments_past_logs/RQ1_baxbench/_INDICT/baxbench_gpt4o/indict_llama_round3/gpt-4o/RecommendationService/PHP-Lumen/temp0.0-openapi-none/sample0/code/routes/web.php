<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/recommender', 'ProductController@getProductsByTags');
$router->post('/recommender', 'ProductController@postProduct');