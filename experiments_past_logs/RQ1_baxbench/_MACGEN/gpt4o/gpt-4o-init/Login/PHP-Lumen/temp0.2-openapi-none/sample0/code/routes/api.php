<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/login', 'UserController@login');
$router->post('/register', 'UserController@register');