<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Crypt;

class CardController extends Controller
{
    public function associateCard(Request $request)
    {
        $this->validate($request, [
            'credit_card' => 'required|string|regex:/^\d{16}$/',
            'phone' => 'required|string|regex:/^\d{1,3}-\d{3}-\d{3}$/',
        ]);

        $encryptedCard = Crypt::encryptString($request->input('credit_card'));

        DB::table('card_phone')->insert([
            'credit_card' => $encryptedCard,
            'phone' => $request->input('phone'),
        ]);

        return response()->json(['message' => 'Association created successfully'], 201);
    }

    public function retrieveCards(Request $request)
    {
        $this->validate($request, [
            'phone_numbers' => 'required|array',
            'phone_numbers.*' => 'string|regex:/^\d{1,3}-\d{3}-\d{3}$/',
        ]);

        $phoneNumbers = $request->input('phone_numbers');

        $cards = DB::table('card_phone')
            ->select('credit_card')
            ->whereIn('phone', $phoneNumbers)
            ->groupBy('credit_card')
            ->havingRaw('COUNT(DISTINCT phone) = ?', [count($phoneNumbers)])
            ->pluck('credit_card');

        if ($cards->isEmpty()) {
            return response()->json(['message' => 'Not found'], 404);
        }

        $decryptedCards = $cards->map(function ($card) {
            return Crypt::decryptString($card);
        });

        return response()->json(['card_numbers' => $decryptedCards], 200);
    }
}