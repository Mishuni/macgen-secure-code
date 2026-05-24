<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    $_SERVER['APP_BASE_PATH'] ?? __DIR__.'/../'
);

// Load environment variables
$app->configure('app');
$app->configure('database');

// Register the database service provider
$app->register(Illuminate\Database\DatabaseServiceProvider::class);

// Register the Eloquent ORM
$app->withFacades();
$app->withEloquent();

return $app;