<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/add', 'ProductController@add');
$router->get('/download', 'ProductController@download');
$router->post('/upload', 'ProductController@upload');
$router->get('/search', 'ProductController@search');