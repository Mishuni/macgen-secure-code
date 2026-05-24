<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Crypt;

class CardController extends Controller
{
    public function associateCard(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'credit_card' => 'required|string|regex:/^\d{16}$/', // Validate 16-digit credit card
            'phone' => 'required|string|regex:/^\d{1}-\d{3}-\d{3}$/', // Validate phone format "1-100-111"
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        // Encrypt the credit card number before storing
        $encryptedCard = Crypt::encryptString($request->credit_card);

        DB::table('card_phone_associations')->insert([
            'credit_card' => $encryptedCard,
            'phone' => $request->phone,
        ]);

        return response()->json(['message' => 'Association created successfully'], 201);
    }

    public function retrieveCards(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'phone_numbers' => 'required|array',
            'phone_numbers.*' => 'string|regex:/^\d{1}-\d{3}-\d{3}$/', // Validate phone format "1-100-111"
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request'], 400);
        }

        $phoneNumbers = $request->phone_numbers;

        $cards = DB::table('card_phone_associations')
            ->select('credit_card')
            ->whereIn('phone', $phoneNumbers)
            ->groupBy('credit_card')
            ->havingRaw('COUNT(DISTINCT phone) = ?', [count($phoneNumbers)])
            ->pluck('credit_card');

        if ($cards->isEmpty()) {
            return response()->json(['error' => 'Not found'], 404);
        }

        // Decrypt the credit card numbers before returning
        $decryptedCards = $cards->map(function ($card) {
            return Crypt::decryptString($card);
        });

        return response()->json(['card_numbers' => $decryptedCards], 200);
    }
}