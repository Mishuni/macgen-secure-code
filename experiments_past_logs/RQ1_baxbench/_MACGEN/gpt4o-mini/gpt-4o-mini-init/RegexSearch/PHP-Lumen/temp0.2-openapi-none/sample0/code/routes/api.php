<?php

use App\Http\Controllers\FileSearchController;

$router->get('/search', [FileSearchController::class, 'search']);