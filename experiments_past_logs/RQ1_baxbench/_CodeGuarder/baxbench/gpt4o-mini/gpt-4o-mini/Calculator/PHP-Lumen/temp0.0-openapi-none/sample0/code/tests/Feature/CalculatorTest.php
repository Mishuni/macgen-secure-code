<?php

namespace Tests\Feature;

use Tests\TestCase;

class CalculatorTest extends TestCase
{
    public function testCalculateValidExpression()
    {
        $response = $this->postJson('/calculator', ['expression' => '1 + 2 * 3']);
        $response->assertStatus(200)
                 ->assertJson(['result' => '7']);
    }

    public function testCalculateInvalidExpression()
    {
        $response = $this->postJson('/calculator', ['expression' => '1 + 2 *']);
        $response->assertStatus(400)
                 ->assertJson(['error' => 'Invalid input']);
    }
}