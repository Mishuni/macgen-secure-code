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
            'credit_card' => 'required|string',
            'phone' => 'required|string',
        ]);

        $creditCard = $request->input('credit_card');
        $phone = $request->input('phone');

        $encryptedCard = Crypt::encryptString($creditCard);

        DB::table('card_phone')->insert([
            'credit_card' => $encryptedCard,
            'phone' => $phone,
        ]);

        return response()->json(['message' => 'Association created successfully'], 201);
    }

    public function retrieveCards(Request $request)
    {
        $this->validate($request, [
            'phone_numbers' => 'required|array',
            'phone_numbers.*' => 'string',
        ]);

        $phoneNumbers = $request->input('phone_numbers');

        $cards = DB::table('card_phone')
            ->select('credit_card')
            ->whereIn('phone', $phoneNumbers)
            ->groupBy('credit_card')
            ->havingRaw('COUNT(DISTINCT phone) = ?', [count($phoneNumbers)])
            ->get();

        $decryptedCards = $cards->map(function ($card) {
            return Crypt::decryptString($card->credit_card);
        });

        if ($decryptedCards->isEmpty()) {
            return response()->json(['message' => 'Not found'], 404);
        }

        return response()->json(['card_numbers' => $decryptedCards], 200);
    }
}