<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\SecretController;

$router->post('/register', [AuthController::class, 'register']);
$router->post('/login', [AuthController::class, 'login']);
$router->post('/set_secret', [SecretController::class, 'setSecret']);
$router->get('/get_secret', [SecretController::class, 'getSecret']);