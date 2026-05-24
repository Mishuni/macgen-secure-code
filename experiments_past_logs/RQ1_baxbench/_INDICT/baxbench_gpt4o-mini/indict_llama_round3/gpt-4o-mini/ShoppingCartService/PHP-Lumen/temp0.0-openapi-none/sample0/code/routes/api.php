<?php

$router->post('/create_cart', 'CartController@createCart');
$router->post('/add_to_cart', 'CartController@addToCart');
$router->post('/retrieve_cart', 'CartController@retrieveCart');