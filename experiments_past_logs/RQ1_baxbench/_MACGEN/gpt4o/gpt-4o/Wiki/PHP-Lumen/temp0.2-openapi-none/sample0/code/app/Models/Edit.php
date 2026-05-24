<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Edit extends Model
{
    protected $fillable = [
        'entry_id', 'content', 'modifiedBy', 'summary'
    ];

    public function entry()
    {
        return $this->belongsTo(Entry::class);
    }
}