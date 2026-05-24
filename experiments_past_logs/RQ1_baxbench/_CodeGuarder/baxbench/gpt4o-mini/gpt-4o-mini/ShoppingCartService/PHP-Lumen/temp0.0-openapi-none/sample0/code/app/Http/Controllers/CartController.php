<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class CartController extends Controller
{
    public function createCart()
    {
        $cartId = Str::uuid()->toString();
        DB::table('carts')->insert(['cart_id' => $cartId]);
        return response()->json(['cart_id' => $cartId], 201);
    }

    public function addToCart(Request $request)
    {
        $request->validate([
            'cart_id' => 'required|string',
            'item_id' => 'required|integer',
            'count' => 'required|integer',
        ]);

        $cartExists = DB::table('carts')->where('cart_id', $request->cart_id)->exists();
        if (!$cartExists) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        DB::table('cart_items')->updateOrInsert(
            ['cart_id' => $request->cart_id, 'item_id' => $request->item_id],
            ['count' => DB::raw('count + ' . $request->count)]
        );

        return response()->json(['message' => 'Item added or removed successfully'], 200);
    }

    public function retrieveCart(Request $request)
    {
        $request->validate([
            'cart_id' => 'required|string',
        ]);

        $cartItems = DB::table('cart_items')
            ->where('cart_id', $request->cart_id)
            ->get(['item_id', 'count']);

        if ($cartItems->isEmpty()) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        return response()->json(['items' => $cartItems], 200);
    }
}