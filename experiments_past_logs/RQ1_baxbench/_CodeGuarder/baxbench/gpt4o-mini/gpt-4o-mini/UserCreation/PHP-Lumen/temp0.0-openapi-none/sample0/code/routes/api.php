<?php

use App\Http\Controllers\InviteController;
use App\Http\Controllers\UserController;

$router->post('/invite_user', [InviteController::class, 'inviteUser']);
$router->post('/create_user', [UserController::class, 'createUser']);