<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Service extends Model
{
    protected $fillable = ['service_id', 'token', 'last_notification'];
    public $timestamps = false;
}