<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    dirname(__DIR__)
);

$app->withFacades();
$app->withEloquent();

$app->configure('app');

$app->routeMiddleware([
    // Add any middleware here if needed
]);

$app->register(App\Providers\AppServiceProvider::class);
$app->register(App\Providers\AuthServiceProvider::class);

$app->group(['namespace' => 'App\Http\Controllers'], function ($app) {
    require_once __DIR__.'/../routes/web.php';
    require_once __DIR__.'/../routes/api.php';
});

return $app;