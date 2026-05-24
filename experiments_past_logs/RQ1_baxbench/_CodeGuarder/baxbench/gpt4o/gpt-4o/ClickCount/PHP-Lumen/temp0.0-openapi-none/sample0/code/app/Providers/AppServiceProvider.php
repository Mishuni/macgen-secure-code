<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AppServiceProvider extends ServiceProvider
{
    public function register()
    {
        //
    }

    public function boot()
    {
        // Create clicks table if it doesn't exist
        Schema::create('clicks', function (Blueprint $table) {
            $table->id();
            $table->timestamp('timestamp');
        });
    }
}