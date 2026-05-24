<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateCreditCardAssociationsTable extends Migration
{
    public function up()
    {
        Schema::create('credit_card_associations', function (Blueprint $table) {
            $table->id();
            $table->string('credit_card', 16);
            $table->string('phone');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('credit_card_associations');
    }
}