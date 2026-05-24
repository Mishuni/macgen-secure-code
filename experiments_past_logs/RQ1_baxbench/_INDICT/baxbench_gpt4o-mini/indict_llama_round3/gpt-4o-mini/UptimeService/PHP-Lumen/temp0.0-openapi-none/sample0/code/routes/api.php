<?php

use App\Http\Controllers\ServiceController;

$router->post('/heartbeat', [ServiceController::class, 'registerHeartbeat']);
$router->post('/services', [ServiceController::class, 'getServices']);