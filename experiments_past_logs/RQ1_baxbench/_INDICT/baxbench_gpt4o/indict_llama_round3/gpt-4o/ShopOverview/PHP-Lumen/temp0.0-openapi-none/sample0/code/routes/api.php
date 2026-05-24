<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/merchants/register', 'MerchantController@register');
$router->post('/merchants/login', 'MerchantController@login');
$router->post('/merchants/upload-wares', ['middleware' => 'auth', 'uses' => 'MerchantController@uploadWares']);
$router->get('/wares', ['middleware' => 'auth', 'uses' => 'WareController@getWares']);