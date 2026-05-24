<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Edit extends Model
{
    protected $fillable = [
        'entry_id', 'content', 'modifiedBy', 'summary', 'modifiedAt'
    ];

    protected $dates = [
        'modifiedAt'
    ];
}