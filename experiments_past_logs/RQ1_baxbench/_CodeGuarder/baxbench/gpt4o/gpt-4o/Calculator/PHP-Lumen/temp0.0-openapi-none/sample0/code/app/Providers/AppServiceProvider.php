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
        // Ensure the SQLite database file exists
        $databasePath = app()->databasePath('db.sqlite3');
        if (!file_exists($databasePath)) {
            touch($databasePath);
        }
    }
}