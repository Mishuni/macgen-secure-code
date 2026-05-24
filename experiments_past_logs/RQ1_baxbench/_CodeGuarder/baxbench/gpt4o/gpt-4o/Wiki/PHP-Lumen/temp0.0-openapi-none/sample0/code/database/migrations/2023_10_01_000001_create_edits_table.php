<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateEditsTable extends Migration
{
    public function up()
    {
        Schema::create('edits', function (Blueprint $table) {
            $table->id();
            $table->uuid('entry_id');
            $table->string('modifiedBy');
            $table->string('summary');
            $table->text('content');
            $table->timestamps();

            $table->foreign('entry_id')->references('id')->on('entries')->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::dropIfExists('edits');
    }
}