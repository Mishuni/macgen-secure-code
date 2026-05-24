<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/monitor/commands', 'MonitorController@getProcesses');