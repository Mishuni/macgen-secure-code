<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateSecretsTable extends Migration
{
    public function up()
    {
        Schema::create('secrets', function (Blueprint $table) {
            $table->id();
            $table->string('username');
            $table->text('secret');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('secrets');
    }
}