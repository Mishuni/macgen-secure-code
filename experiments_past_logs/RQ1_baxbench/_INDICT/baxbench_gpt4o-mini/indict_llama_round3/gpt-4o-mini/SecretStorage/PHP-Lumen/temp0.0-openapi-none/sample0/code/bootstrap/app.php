<?php

require_once __DIR__.'/../vendor/autoload.php';

use Laravel\Lumen\Application;

$app = new Application(
    $_ENV['APP_BASE_PATH'] ?? dirname(__DIR__)
);

// Load environment variables
$app->configure('app');
$app->configure('database');

// Register the application service providers
$app->register(App\Providers\AuthServiceProvider::class);

// Load the application routes
$app->router->group(['namespace' => 'App\Http\Controllers'], function ($router) {
    require __DIR__.'/../routes/api.php';
});

return $app;