<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     *
     * @return void
     */
    public function register()
    {
        //
    }

    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot()
    {
        // Ensure SQLite foreign key constraints are enabled
        if (config('database.default') === 'sqlite') {
            \DB::statement(\DB::raw('PRAGMA foreign_keys=ON'));
        }
    }
}