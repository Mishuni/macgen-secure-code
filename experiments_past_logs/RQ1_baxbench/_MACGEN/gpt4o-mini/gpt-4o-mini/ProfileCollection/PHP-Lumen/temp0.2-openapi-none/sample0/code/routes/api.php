<?php

use App\Http\Controllers\ProfileController;

$router->post('/add_profile', [ProfileController::class, 'addProfile']);
$router->get('/profile/{username}', [ProfileController::class, 'getProfile']);
$router->get('/profile-photo/{username}', [ProfileController::class, 'getProfilePhoto']);