<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/log', 'LogController@store');
$router->get('/logs', 'LogController@index');