<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Click extends Model
{
    protected $fillable = ['timestamp'];

    public $timestamps = false; // Disable timestamps since we are not using created_at and updated_at

    protected $primaryKey = 'id'; // Explicitly define primary key
}