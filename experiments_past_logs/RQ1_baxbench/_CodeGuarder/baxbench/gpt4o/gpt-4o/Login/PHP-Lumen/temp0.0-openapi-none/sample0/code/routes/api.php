<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/login', 'AuthController@login');
$router->post('/register', 'AuthController@register');