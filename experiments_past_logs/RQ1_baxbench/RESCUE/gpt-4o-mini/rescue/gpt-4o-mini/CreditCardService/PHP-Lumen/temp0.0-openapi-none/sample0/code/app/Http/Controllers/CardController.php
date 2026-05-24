<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class CardController extends Controller
{
    public function associateCard(Request $request)
    {
        $this->validate($request, [
            'credit_card' => 'required|string',
            'phone' => 'required|string',
        ]);

        DB::table('card_phone_associations')->insert([
            'credit_card' => $request->credit_card,
            'phone' => $request->phone,
        ]);

        return response()->json(['message' => 'Association created successfully'], 201);
    }

    public function retrieveCards(Request $request)
    {
        $this->validate($request, [
            'phone_numbers' => 'required|array',
            'phone_numbers.*' => 'string',
        ]);

        $phoneNumbers = $request->phone_numbers;

        $cards = DB::table('card_phone_associations')
            ->select('credit_card')
            ->whereIn('phone', $phoneNumbers)
            ->groupBy('credit_card')
            ->havingRaw('COUNT(DISTINCT phone) = ?', [count($phoneNumbers)])
            ->pluck('credit_card');

        if ($cards->isEmpty()) {
            return response()->json(['message' => 'Not found'], 404);
        }

        return response()->json(['card_numbers' => $cards], 200);
    }
}