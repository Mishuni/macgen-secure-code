<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Service extends Model
{
    protected $table = 'services';
    protected $fillable = ['serviceId', 'lastNotification', 'token'];
    public $timestamps = false; // We are not using created_at and updated_at
}