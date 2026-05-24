<?php

require_once __DIR__.'/../vendor/autoload.php';

use Laravel\Lumen\Application;

$app = new Application(
    $_ENV['APP_BASE_PATH'] ?? dirname(__DIR__)
);

// Load environment variables
$app->configure('app');
$app->configure('auth');
$app->configure('database');

// Register the application service providers
$app->register(App\Providers\AppServiceProvider::class);
$app->register(App\Providers\AuthServiceProvider::class);

// Set up the database connection
$app->make('db')->setConfig([
    'driver' => 'sqlite',
    'database' => database_path('db.sqlite3'),
]);

return $app;