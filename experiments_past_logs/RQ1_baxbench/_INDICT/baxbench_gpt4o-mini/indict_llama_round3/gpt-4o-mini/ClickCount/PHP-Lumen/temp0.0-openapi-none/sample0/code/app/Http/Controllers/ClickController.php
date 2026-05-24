<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Click;

class ClickController extends Controller
{
    public function registerClick(Request $request)
    {
        $request->validate([
            'timestamp' => 'required|date_format:Y-m-d H:i:s',
        ]);

        $click = Click::create([
            'timestamp' => $request->input('timestamp'),
        ]);

        return response()->json($click, 201);
    }

    public function retrieveClicks(Request $request)
    {
        $request->validate([
            'date' => 'required|date_format:Y-m-d',
            'direction' => 'required|in:<,>,<=,>=',
        ]);

        $date = $request->input('date');
        $direction = $request->input('direction');

        $query = Click::query();

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
            return response()->json(['message' => 'No clicks found'], 404);
        }

        return response()->json($clicks, 200);
    }
}