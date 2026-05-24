<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class CardController extends Controller
{
    /**
     * Associate a credit card with a phone number.
     */
    public function associateCard(Request $request)
    {
        $this->validate($request, [
            'credit_card' => 'required|string|regex:/^\d{16}$/',
            'phone' => 'required|string|regex:/^\d{1,4}-\d{1,4}-\d{1,4}$/',
        ]);

        $creditCard = $request->input('credit_card');
        $phone = $request->input('phone');

        DB::table('card_phone_associations')->insert([
            'credit_card' => $creditCard,
            'phone' => $phone,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['message' => 'Association created successfully'], 201);
    }

    /**
     * Retrieve credit cards associated with a set of phone numbers.
     */
    public function retrieveCards(Request $request)
    {
        $this->validate($request, [
            'phone_numbers' => 'required|array|min:1',
            'phone_numbers.*' => 'string|regex:/^\d{1,4}-\d{1,4}-\d{1,4}$/',
        ]);

        $phoneNumbers = $request->input('phone_numbers');

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