<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Comment extends Model
{
    protected $fillable = ['recipe_id', 'comment'];

    public function recipe()
    {
        return $this->belongsTo(Recipe::class);
    }
}