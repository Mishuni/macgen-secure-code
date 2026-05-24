<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/click', 'ClickController@registerClick');
$router->get('/clicks', 'ClickController@retrieveClicks');