<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    protected $fillable = ['email', 'username', 'password', 'secret'];

    protected $hidden = ['password'];
}