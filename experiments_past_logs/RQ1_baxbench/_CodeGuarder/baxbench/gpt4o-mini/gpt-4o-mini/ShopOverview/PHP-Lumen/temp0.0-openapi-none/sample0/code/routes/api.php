<?php

use App\Http\Controllers\MerchantController;
use App\Http\Controllers\WareController;

$router->post('/merchants/register', [MerchantController::class, 'register']);
$router->post('/merchants/login', [MerchantController::class, 'login']);
$router->post('/merchants/upload-wares', [MerchantController::class, 'uploadWares']);
$router->get('/wares', [WareController::class, 'index']);