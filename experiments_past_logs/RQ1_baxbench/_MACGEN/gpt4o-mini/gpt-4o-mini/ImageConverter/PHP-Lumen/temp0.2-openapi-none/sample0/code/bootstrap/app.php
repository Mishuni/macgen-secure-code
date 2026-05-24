<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Laravel\Lumen\Application(
    dirname(__DIR__)
);

$app->withFacades();
$app->withEloquent();

$app->configure('app');
$app->configure('database');

$app->register(App\Providers\AppServiceProvider::class);
$app->register(App\Providers\AuthServiceProvider::class);

$app->register(Illuminate\Database\DatabaseServiceProvider::class);

$app->make('db')->setConfig([
    'driver' => 'sqlite',
    'database' => database_path('db.sqlite3'),
    'prefix' => '',
]);

return $app;