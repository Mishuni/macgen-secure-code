<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    $_SERVER['APP_BASE_PATH'] ?? __DIR__.'/../'
);

$app->withFacades();
$app->withEloquent();

$app->configure('database');

$app->register(App\Providers\AppServiceProvider::class);

return $app;