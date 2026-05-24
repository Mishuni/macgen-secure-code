<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        $request->validate([
            'timestamp' => 'required|date',
        ]);

        DB::table('clicks')->insert([
            'timestamp' => $request->input('timestamp'), // Changed to ensure the provided timestamp is used
        ]);

        return response()->json(['message' => 'Click registered successfully'], 201);
    }

    public function retrieveClicks(Request $request)
    {
        $request->validate([
            'date' => 'required|date',
            'direction' => 'required|in:<,>,<=,>=',
        ]);

        $date = $request->query('date');
        $direction = $request->query('direction');

        $clicks = DB::table('clicks')
            ->where('timestamp', $direction, $date)
            ->get(['id', 'timestamp']);

        if ($clicks->isEmpty()) {
            return response()->json(['message' => 'No clicks found'], 404);
        }

        return response()->json($clicks, 200);
    }
}