<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class CartController extends Controller
{
    public function createCart(Request $request)
    {
        $cartId = uniqid('cart_');
        DB::table('carts')->insert(['cart_id' => $cartId]);

        return response()->json(['cart_id' => $cartId], 201);
    }

    public function addToCart(Request $request)
    {
        $request->validate([
            'cart_id' => 'required|string',
            'item_id' => 'required|integer|min:1',
            'count' => 'required|integer',
        ]);

        $cart = DB::table('carts')->where('cart_id', $request->cart_id)->first();
        if (!$cart) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $item = DB::table('cart_items')->where('cart_id', $cart->id)->where('item_id', $request->item_id)->first();
        if ($item) {
            $newCount = $item->count + $request->count;
            if ($newCount <= 0) {
                DB::table('cart_items')->where('id', $item->id)->delete();
            } else {
                DB::table('cart_items')->where('id', $item->id)->update(['count' => $newCount]);
            }
        } else {
            if ($request->count > 0) {
                DB::table('cart_items')->insert([
                    'cart_id' => $cart->id,
                    'item_id' => $request->item_id,
                    'count' => $request->count,
                ]);
            }
        }

        return response()->json([], 200);
    }

    public function retrieveCart(Request $request)
    {
        $request->validate(['cart_id' => 'required|string']);

        $cart = DB::table('carts')->where('cart_id', $request->cart_id)->first();
        if (!$cart) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $items = DB::table('cart_items')->where('cart_id', $cart->id)->get(['item_id', 'count']);

        return response()->json(['items' => $items], 200);
    }
}