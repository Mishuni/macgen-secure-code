<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/heartbeat', 'ServiceController@registerHeartbeat');
$router->post('/services', 'ServiceController@getServices');