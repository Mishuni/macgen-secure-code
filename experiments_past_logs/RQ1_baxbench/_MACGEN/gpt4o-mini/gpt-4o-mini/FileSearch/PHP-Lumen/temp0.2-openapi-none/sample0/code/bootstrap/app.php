<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    $_SERVER['APP_BASE_PATH'] ?? __DIR__.'/../'
);

$app->withFacades();
$app->withEloquent();

$app->configure('app');

$app->routeMiddleware([
    // Add any middleware here if needed
]);

$app->register(App\Providers\AppServiceProvider::class);
$app->register(App\Providers\AuthServiceProvider::class);

$app->register(Laravel\Lumen\Providers\EventServiceProvider::class);
$app->register(Laravel\Lumen\Providers\RouteServiceProvider::class);

return $app;