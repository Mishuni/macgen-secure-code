<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    protected $fillable = ['email', 'username', 'password'];

    // Disable timestamps if not needed
    public $timestamps = false;
}