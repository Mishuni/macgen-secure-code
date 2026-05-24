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
        // Enable SQLite foreign key constraints
        if (env('DB_CONNECTION') === 'sqlite') {
            \DB::statement('PRAGMA foreign_keys=ON');
        }
    }
}