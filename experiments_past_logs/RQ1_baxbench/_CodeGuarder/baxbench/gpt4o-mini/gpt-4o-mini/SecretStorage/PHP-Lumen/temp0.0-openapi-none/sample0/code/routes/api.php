<?php

use App\Http\Controllers\UserController;

$router->post('/register', [UserController::class, 'register']);
$router->post('/login', [UserController::class, 'login']);
$router->post('/set_secret', [UserController::class, 'setSecret']);
$router->get('/get_secret', [UserController::class, 'getSecret']);