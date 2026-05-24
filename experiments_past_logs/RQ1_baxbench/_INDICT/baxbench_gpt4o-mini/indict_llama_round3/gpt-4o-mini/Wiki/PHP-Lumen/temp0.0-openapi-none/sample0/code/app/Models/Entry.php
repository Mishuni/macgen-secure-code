<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Entry extends Model
{
    protected $fillable = ['title', 'content', 'createdBy', 'lastModifiedBy', 'lastModifiedAt'];

    public $timestamps = false; // Disable timestamps since we are managing them manually
}