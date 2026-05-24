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
        // Ensure SQLite foreign key constraints are enabled
        if (env('DB_CONNECTION') === 'sqlite') {
            \DB::statement(\DB::raw('PRAGMA foreign_keys=ON'));
        }
    }
}