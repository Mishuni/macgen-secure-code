<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

class ClickFactory extends Factory
{
    protected $model = \App\Models\Click::class;

    public function definition()
    {
        return [
            'timestamp' => now(),
        ];
    }
}