<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Ware extends Model
{
    protected $fillable = ['name', 'description', 'price', 'merchant_id'];

    public function merchant()
    {
        return $this->belongsTo(Merchant::class);
    }
}