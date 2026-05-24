<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register()
    {
        //
    }

    public function boot()
    {
        // Set the default string length for database migrations
        \Illuminate\Database\Schema\Blueprint::macro('string', function ($column, $length = 255) {
            return $this->addColumn('string', $column, compact('length'));
        });
    }
}