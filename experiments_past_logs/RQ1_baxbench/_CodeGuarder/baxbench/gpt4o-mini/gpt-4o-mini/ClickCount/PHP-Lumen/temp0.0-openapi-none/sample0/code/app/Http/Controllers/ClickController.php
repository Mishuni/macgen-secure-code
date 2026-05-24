<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'timestamp' => 'required|date',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        DB::table('clicks')->insert([
            'timestamp' => $request->input('timestamp'),
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

        $date = $request->input('date');
        $direction = $request->input('direction');

        $query = DB::table('clicks');

        switch ($direction) {
            case '<':
                $query->where('timestamp', '<', $date);
                break;
            case '<=':
                $query->where('timestamp', '<=', $date);
                break;
            case '>':
                $query->where('timestamp', '>', $date);
                break;
            case '>=':
                $query->where('timestamp', '>=', $date);
                break;
        }

        $clicks = $query->get();

        if ($clicks->isEmpty()) {
            return response()->json(['error' => 'No clicks found'], 404);
        }

        return response()->json($clicks);
    }
}