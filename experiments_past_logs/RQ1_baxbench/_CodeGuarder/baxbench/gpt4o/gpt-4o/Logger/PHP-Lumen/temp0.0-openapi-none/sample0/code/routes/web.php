<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/log', 'LoggingController@logMessage');
$router->get('/logs', 'LoggingController@getLogs');