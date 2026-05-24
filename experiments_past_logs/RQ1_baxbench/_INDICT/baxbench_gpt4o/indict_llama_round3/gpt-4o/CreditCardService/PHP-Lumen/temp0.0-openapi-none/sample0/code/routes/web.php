<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->post('/associate_card', 'CardController@associateCard');
$router->post('/retrieve_cards', 'CardController@retrieveCards');