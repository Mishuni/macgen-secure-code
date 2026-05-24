<?php

/** @var \Laravel\Lumen\Routing\Router $router */

$router->get('/', function () {
    return response()->json(['message' => 'Welcome to the PDF to Text Converter API']);
});