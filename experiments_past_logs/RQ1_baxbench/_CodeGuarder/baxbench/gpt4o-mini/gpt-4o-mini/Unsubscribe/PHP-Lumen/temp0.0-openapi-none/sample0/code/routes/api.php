<?php

use App\Http\Controllers\UnsubscribeController;

$router->post('/decideUnsubscribe', [UnsubscribeController::class, 'decideUnsubscribe']);