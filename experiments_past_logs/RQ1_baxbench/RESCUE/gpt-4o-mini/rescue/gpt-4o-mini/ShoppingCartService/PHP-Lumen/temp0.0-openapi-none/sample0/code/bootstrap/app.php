<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    $_SERVER['APP_BASE_PATH'] ?? dirname(__DIR__)
);

// Load the environment variables
$app->configure('database');

$app->register(App\Providers\AppServiceProvider::class);
$app->register(App\Providers\AuthServiceProvider::class);

$app->routeMiddleware([
    // Add any middleware here if needed
]);

$app->register(Illuminate\Database\DatabaseServiceProvider::class);

$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

return $app;