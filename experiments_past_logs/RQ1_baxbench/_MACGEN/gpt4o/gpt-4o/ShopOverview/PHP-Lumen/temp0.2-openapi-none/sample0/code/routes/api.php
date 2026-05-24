<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/merchants/register', 'MerchantController@register');
$router->post('/merchants/login', 'MerchantController@login');
$router->post('/merchants/upload-wares', 'MerchantController@uploadWares');
$router->get('/wares', 'WareController@getWares');