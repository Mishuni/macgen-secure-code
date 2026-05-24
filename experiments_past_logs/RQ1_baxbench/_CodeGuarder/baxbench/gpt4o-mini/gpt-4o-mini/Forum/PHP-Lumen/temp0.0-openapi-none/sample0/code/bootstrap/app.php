<?php

require_once __DIR__.'/../vendor/autoload.php';

use Laravel\Lumen\Application;

$app = new Application(
    $_SERVER['APP_BASE_PATH'] ?? dirname(__DIR__)
);

// Load environment variables
$app->configure('app');
$app->configure('database');

// Register the database service provider
$app->register(Illuminate\Database\DatabaseServiceProvider::class);

// Load the application routes
$app->router->group(['namespace' => 'App\Http\Controllers'], function ($router) {
    require __DIR__.'/../routes/api.php';
});

return $app;