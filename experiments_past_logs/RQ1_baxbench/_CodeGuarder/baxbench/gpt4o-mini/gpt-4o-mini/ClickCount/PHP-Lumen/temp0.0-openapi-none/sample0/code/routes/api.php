<?php

use App\Http\Controllers\ClickController;

$router->post('/click', [ClickController::class, 'registerClick']);
$router->get('/clicks', [ClickController::class, 'retrieveClicks']);