<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ClickController extends Controller
{
    /**
     * Register a user's click.
     */
    public function registerClick(Request $request)
    {
        try {
            $timestamp = now();

            DB::insert('INSERT INTO clicks (timestamp) VALUES (?)', [$timestamp]);

            return response()->json(['message' => 'Click registered successfully'], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to register click'], 400);
        }
    }

    /**
     * Retrieve clicks based on date and direction.
     */
    public function getClicks(Request $request)
    {
        $date = $request->query('date');
        $direction = $request->query('direction');

        if (!$date || !$direction || !in_array($direction, ['<', '<=', '>', '>='])) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        try {
            $clicks = DB::select("SELECT * FROM clicks WHERE timestamp $direction ?", [$date]);

            if (empty($clicks)) {
                return response()->json(['error' => 'No clicks found'], 404);
            }

            return response()->json($clicks, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to retrieve clicks'], 400);
        }
    }
}