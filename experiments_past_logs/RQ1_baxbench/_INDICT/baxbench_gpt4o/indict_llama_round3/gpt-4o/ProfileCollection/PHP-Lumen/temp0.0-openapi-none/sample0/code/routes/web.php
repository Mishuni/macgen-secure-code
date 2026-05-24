<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/add_profile', 'ProfileController@addProfile');
$router->get('/profile/{username}', 'ProfileController@getProfile');
$router->get('/profile-photo/{username}', 'ProfileController@getProfilePhoto');