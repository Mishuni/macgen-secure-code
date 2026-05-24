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
        // Set the default string length for database columns
        \Illuminate\Database\Schema\Blueprint::defaultStringLength(191);
    }
}