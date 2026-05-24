<?php

namespace App\Http\Controllers;

use App\Models\Click;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        $request->validate([
            'timestamp' => 'required|date',
        ]);

        $click = new Click();
        $click->timestamp = $request->input('timestamp');
        $click->save();

        return response()->json(['message' => 'Click registered successfully'], 201);
    }

    public function retrieveClicks(Request $request)
    {
        $request->validate([
            'date' => 'required|date',
            'direction' => 'required|in:<,<=,>,>=',
        ]);

        $date = $request->input('date');
        $direction = $request->input('direction');

        $operator = $direction === '<' ? '<' : ($direction === '<=' ? '<=' : ($direction === '>' ? '>' : '>='));

        $clicks = DB::table('clicks')
            ->where('timestamp', $operator, $date)
            ->get();

        if ($clicks->isEmpty()) {
            return response()->json(['message' => 'No clicks found'], 404);
        }

        return response()->json($clicks, 200);
    }
}