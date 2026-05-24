<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Cart extends Model
{
    protected $fillable = ['cart_id'];
    public $incrementing = false;
    protected $primaryKey = 'cart_id';
    protected $keyType = 'string';
}