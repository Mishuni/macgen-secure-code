<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateCardPhoneAssociationsTable extends Migration
{
    public function up()
    {
        Schema::create('card_phone_associations', function (Blueprint $table) {
            $table->id();
            $table->string('credit_card');
            $table->string('phone');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('card_phone_associations');
    }
}