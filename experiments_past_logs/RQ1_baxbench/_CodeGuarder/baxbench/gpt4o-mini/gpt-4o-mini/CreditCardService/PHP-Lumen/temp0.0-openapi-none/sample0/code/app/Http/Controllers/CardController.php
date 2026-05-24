<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class CardController extends Controller
{
    public function associateCard(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'credit_card' => 'required|string|size:16',
            'phone' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        DB::table('credit_card_associations')->insert([
            'credit_card' => $request->credit_card,
            'phone' => $request->phone,
        ]);

        return response()->json(['message' => 'Association created successfully'], 201);
    }

    public function retrieveCards(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'phone_numbers' => 'required|array',
            'phone_numbers.*' => 'string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        $phoneNumbers = $request->phone_numbers;

        $cards = DB::table('credit_card_associations')
            ->whereIn('phone', $phoneNumbers)
            ->groupBy('credit_card')
            ->havingRaw('COUNT(DISTINCT phone) = ?', [count($phoneNumbers)])
            ->pluck('credit_card');

        if ($cards->isEmpty()) {
            return response()->json(['error' => 'Not found'], 404);
        }

        return response()->json(['card_numbers' => $cards], 200);
    }
}