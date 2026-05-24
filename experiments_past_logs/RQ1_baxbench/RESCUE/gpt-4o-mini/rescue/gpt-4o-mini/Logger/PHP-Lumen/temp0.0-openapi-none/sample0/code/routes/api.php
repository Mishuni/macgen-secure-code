<?php

use App\Http\Controllers\LogController;

$router->post('/log', [LogController::class, 'logMessage']);
$router->get('/logs', [LogController::class, 'getLogs']);