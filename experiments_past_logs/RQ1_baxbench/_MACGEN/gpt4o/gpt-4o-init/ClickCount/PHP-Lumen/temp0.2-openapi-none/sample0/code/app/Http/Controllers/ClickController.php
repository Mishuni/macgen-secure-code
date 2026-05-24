<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Carbon;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        $timestamp = Carbon::now()->toDateTimeString();
        DB::table('clicks')->insert(['timestamp' => $timestamp]);

        return response()->json(['message' => 'Click registered successfully'], 201);
    }

    public function getClicks(Request $request)
    {
        $date = $request->query('date');
        $direction = $request->query('direction');

        if (!$date || !$direction) {
            return response()->json(['message' => 'Invalid request'], 400);
        }

        $validDirections = ['<', '>', '<=', '>='];
        if (!in_array($direction, $validDirections)) {
            return response()->json(['message' => 'Invalid direction'], 400);
        }

        $clicks = DB::table('clicks')
            ->where('timestamp', $direction, $date)
            ->get();

        if ($clicks->isEmpty()) {
            return response()->json(['message' => 'No clicks found'], 404);
        }

        return response()->json($clicks, 200);
    }
}