<?php

use App\Http\Controllers\InviteController;

$router->post('/invite_user', [InviteController::class, 'inviteUser']);
$router->post('/create_user', [InviteController::class, 'createUser']);