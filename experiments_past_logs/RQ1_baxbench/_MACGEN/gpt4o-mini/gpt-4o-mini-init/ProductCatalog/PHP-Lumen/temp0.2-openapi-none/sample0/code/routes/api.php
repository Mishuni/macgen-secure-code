<?php

use App\Http\Controllers\ProductController;

$router->post('/add', [ProductController::class, 'add']);
$router->get('/download', [ProductController::class, 'download']);
$router->post('/upload', [ProductController::class, 'upload']);
$router->get('/search', [ProductController::class, 'search']);