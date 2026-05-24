<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/invite_user', 'UserController@inviteUser');
$router->post('/create_user', 'UserController@createUser');