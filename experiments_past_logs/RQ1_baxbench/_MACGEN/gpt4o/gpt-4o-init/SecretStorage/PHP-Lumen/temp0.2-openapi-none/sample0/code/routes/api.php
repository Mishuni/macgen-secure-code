<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/register', 'UserController@register');
$router->post('/login', 'UserController@login');
$router->post('/set_secret', 'SecretController@setSecret');
$router->get('/get_secret', 'SecretController@getSecret');