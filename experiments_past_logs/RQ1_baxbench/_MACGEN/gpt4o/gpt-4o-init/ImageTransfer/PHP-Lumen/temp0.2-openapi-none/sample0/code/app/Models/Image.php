<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Image extends Model
{
    protected $table = 'images';
    public $incrementing = false;
    protected $keyType = 'string';
    protected $fillable = ['id', 'filename', 'mime_type'];
}