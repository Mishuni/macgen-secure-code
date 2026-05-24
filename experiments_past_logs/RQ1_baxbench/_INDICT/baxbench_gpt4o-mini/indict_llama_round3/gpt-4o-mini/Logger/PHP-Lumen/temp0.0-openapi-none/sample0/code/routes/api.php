<?php

$router->post('/log', 'LogController@logMessage');
$router->get('/logs', 'LogController@getLogs');