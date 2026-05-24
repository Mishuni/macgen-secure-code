<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateClicksTable extends Migration
{
    public function up()
    {
        Schema::create('clicks', function (Blueprint $table) {
            $table->id();
            $table->timestamp('timestamp')->index(); // Index the timestamp for improved query performance
        });
    }

    public function down()
    {
        Schema::dropIfExists('clicks');
    }
}