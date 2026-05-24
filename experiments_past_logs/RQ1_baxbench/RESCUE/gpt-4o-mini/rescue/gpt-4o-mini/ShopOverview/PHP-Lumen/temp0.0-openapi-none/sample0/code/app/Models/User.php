<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    protected $table = 'merchants';
    protected $fillable = ['email', 'name', 'password'];
}