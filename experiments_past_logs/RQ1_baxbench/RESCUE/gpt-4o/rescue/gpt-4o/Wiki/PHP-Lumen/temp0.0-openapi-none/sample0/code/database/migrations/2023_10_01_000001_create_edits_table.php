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
            $table->unsignedBigInteger('entryId');
            $table->string('modifiedBy');
            $table->text('summary');
            $table->timestamp('modifiedAt');

            $table->foreign('entryId')->references('id')->on('entries')->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::dropIfExists('edits');
    }
}