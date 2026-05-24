<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/register', 'AuthController@register');
$router->post('/login', 'AuthController@login');
$router->post('/set_secret', 'SecretController@setSecret');
$router->get('/get_secret', 'SecretController@getSecret');