<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateCardPhoneAssociationsTable extends Migration
{
    /**
     * Run the migrations.
     */
    public function up()
    {
        Schema::create('card_phone_associations', function (Blueprint $table) {
            $table->id();
            $table->string('credit_card', 16);
            $table->string('phone', 15);
            $table->timestamps();

            $table->index(['credit_card', 'phone']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down()
    {
        Schema::dropIfExists('card_phone_associations');
    }
}