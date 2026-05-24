<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Product extends Model
{
    protected $fillable = ['name', 'data'];

    protected $casts = [
        'data' => 'array', // Automatically cast JSON to array
    ];
}