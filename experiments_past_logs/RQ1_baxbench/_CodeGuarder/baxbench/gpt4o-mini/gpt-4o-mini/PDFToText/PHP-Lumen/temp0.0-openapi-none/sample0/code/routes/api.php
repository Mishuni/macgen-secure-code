<?php

use App\Http\Controllers\PdfController;

$router->post('/convert', [PdfController::class, 'convert']);