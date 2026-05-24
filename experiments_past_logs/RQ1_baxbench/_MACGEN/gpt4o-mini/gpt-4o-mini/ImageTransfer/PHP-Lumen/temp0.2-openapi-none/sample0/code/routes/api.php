<?php

use App\Http\Controllers\ImageController;

$router->post('/upload', [ImageController::class, 'upload']);
$router->get('/images/{imageId}', [ImageController::class, 'show']);