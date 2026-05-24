<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/add', 'ProductController@addProduct');
$router->get('/download', 'ProductController@downloadProduct');
$router->post('/upload', 'ProductController@uploadProduct');
$router->get('/search', 'ProductController@searchProducts');