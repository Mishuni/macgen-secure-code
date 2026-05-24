<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    protected $fillable = ['username', 'profile_page', 'profile_photo'];
    public $timestamps = false;
}