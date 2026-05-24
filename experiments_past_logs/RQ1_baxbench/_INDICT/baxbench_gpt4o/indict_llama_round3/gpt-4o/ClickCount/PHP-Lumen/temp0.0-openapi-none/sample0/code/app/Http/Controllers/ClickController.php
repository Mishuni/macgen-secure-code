<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Carbon\Carbon;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        $timestamp = Carbon::now('UTC'); // Use UTC for consistency

        DB::table('clicks')->insert([
            'timestamp' => $timestamp,
        ]);

        return response()->json(['message' => 'Click registered successfully'], 201);
    }

    public function retrieveClicks(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'date' => 'required|date',
            'direction' => 'required|in:<,>,<=,>=',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        $date = Carbon::parse($request->input('date'))->setTimezone('UTC');
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