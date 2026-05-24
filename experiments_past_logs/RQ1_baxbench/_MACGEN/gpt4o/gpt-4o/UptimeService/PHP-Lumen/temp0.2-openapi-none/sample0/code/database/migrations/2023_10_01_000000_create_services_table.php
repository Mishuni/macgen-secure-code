<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateServicesTable extends Migration
{
    public function up()
    {
        Schema::create('services', function (Blueprint $table) {
            $table->id();
            $table->string('service_id');
            $table->string('token');
            $table->timestamp('last_notification')->nullable();
        });
    }

    public function down()
    {
        Schema::dropIfExists('services');
    }
}