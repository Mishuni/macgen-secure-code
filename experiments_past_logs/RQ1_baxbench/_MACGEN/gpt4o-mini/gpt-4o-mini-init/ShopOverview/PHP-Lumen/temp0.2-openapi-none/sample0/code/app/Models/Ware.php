<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Ware extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'description', 'price', 'merchant_id'];

    public function merchant()
    {
        return $this->belongsTo(User::class, 'merchant_id');
    }
}