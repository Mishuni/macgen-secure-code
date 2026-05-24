<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Merchant extends Model
{
    protected $fillable = ['email', 'name', 'password'];

    public function wares()
    {
        return $this->hasMany(Ware::class);
    }
}