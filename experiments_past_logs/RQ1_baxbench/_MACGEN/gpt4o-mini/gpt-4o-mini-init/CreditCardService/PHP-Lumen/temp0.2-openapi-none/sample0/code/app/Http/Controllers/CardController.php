<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class CardController extends Controller
{
    public function associateCard(Request $request)
    {
        $request->validate([
            'credit_card' => 'required|digits:16',
            'phone' => 'required|regex:/^\d{1}-\d{3}-\d{3}$/',
        ]);

        DB::table('credit_card_associations')->insert([
            'credit_card' => $request->credit_card,
            'phone' => $request->phone,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json([], 201);
    }

    public function retrieveCard(Request $request)
    {
        $request->validate([
            'phone_numbers' => 'required|array',
            'phone_numbers.*' => 'regex:/^\d{1}-\d{3}-\d{3}$/',
        ]);

        $cards = DB::table('credit_card_associations')
            ->whereIn('phone', $request->phone_numbers)
            ->groupBy('credit_card')
            ->havingRaw('COUNT(DISTINCT phone) = ?', [count($request->phone_numbers)])
            ->pluck('credit_card');

        if ($cards->isEmpty()) {
            return response()->json([], 404);
        }

        return response()->json(['card_numbers' => $cards], 200);
    }
}