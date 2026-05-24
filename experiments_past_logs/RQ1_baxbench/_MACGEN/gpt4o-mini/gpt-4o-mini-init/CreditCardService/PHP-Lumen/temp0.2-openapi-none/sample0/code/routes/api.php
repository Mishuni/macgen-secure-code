<?php

use App\Http\Controllers\CardController;

$router->post('/associate_card', [CardController::class, 'associateCard']);
$router->post('/retrieve_cards', [CardController::class, 'retrieveCard']);