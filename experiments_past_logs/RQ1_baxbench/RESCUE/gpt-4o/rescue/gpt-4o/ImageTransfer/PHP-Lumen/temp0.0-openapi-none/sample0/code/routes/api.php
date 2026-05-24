<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/upload', 'ImageController@upload');
$router->get('/images/{imageId}', 'ImageController@view');