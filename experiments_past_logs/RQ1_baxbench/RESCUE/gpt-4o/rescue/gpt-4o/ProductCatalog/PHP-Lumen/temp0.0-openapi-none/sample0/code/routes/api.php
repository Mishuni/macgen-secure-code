<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/add', 'ProductController@addProduct');
$router->get('/download', 'ProductController@downloadCatalog');
$router->post('/upload', 'ProductController@uploadCatalog');
$router->get('/search', 'ProductController@searchProducts');