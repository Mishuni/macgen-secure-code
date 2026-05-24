<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateServicesTable extends Migration
{
    public function up()
    {
        Schema::create('services', function (Blueprint $table) {
            $table->string('serviceId')->primary();
            $table->timestamp('lastNotification')->nullable();
            $table->string('token');
        });
    }

    public function down()
    {
        Schema::dropIfExists('services');
    }
}