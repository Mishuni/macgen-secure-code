<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Rating extends Model
{
    protected $fillable = ['recipe_id', 'rating'];

    public function recipe()
    {
        return $this->belongsTo(Recipe::class);
    }
}