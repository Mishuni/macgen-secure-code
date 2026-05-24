<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Tag extends Model
{
    protected $fillable = ['name'];

    public function product()
    {
        return $this->belongsTo(Product::class);
    }
}