<?php

use App\Http\Controllers\HeartbeatController;
use App\Http\Controllers\ServicesOverviewController;

$router->post('/heartbeat', [HeartbeatController::class, 'registerHeartbeat']);
$router->post('/services', [ServicesOverviewController::class, 'getServicesOverview']);