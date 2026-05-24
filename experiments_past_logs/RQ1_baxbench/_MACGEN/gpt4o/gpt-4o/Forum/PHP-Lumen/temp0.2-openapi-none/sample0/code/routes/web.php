<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/messages', 'MessageController@getMessages');
$router->post('/messages', 'MessageController@postMessage');