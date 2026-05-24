<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        // Validate request
        $validator = Validator::make($request->all(), [
            'timestamp' => 'required|date_format:Y-m-d\TH:i:sP',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        // Insert click into database
        DB::table('clicks')->insert([
            'timestamp' => $request->input('timestamp'),
        ]);

        return response()->json(['message' => 'Click registered successfully'], 201);
    }

    public function retrieveClicks(Request $request)
    {
        // Validate request
        $validator = Validator::make($request->all(), [
            'date' => 'required|date',
            'direction' => 'required|in:<,>,<=,>=',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        // Retrieve clicks based on query parameters
        $date = $request->input('date');
        $direction = $request->input('direction');

        $clicks = DB::table('clicks')
            ->where('timestamp', $direction, $date)
            ->get();

        if ($clicks->isEmpty()) {
            return response()->json(['error' => 'No clicks found'], 404);
        }

        return response()->json($clicks, 200);
    }
}