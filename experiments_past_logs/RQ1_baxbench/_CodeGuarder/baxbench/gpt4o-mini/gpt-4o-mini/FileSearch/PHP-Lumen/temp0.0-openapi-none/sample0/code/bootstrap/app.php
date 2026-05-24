<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    $_SERVER['APP_BASE_PATH'] ?? dirname(__DIR__)
);

$app->withFacades();
$app->withEloquent();

$app->configure('app');
$app->configure('database');

$app->register(App\Providers\AppServiceProvider::class);
$app->register(App\Providers\AuthServiceProvider::class);

$app->routeMiddleware([
    'auth' => App\Http\Middleware\Authenticate::class,
]);

$app->router->group(['namespace' => 'App\Http\Controllers'], function ($router) {
    require __DIR__.'/../routes/api.php';
});

return $app;