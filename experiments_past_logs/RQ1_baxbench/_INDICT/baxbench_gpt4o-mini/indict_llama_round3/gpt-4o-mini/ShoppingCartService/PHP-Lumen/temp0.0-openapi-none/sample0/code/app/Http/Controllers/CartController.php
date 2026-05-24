<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class CartController extends Controller
{
    public function createCart()
    {
        $cartId = uniqid('cart_');
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

        $item = DB::table('cart_items')->where('cart_id', $request->cart_id)->where('item_id', $request->item_id)->first();

        if ($item) {
            $newCount = $item->count + $request->count;
            if ($newCount <= 0) {
                DB::table('cart_items')->where('cart_id', $request->cart_id)->where('item_id', $request->item_id)->delete();
            } else {
                DB::table('cart_items')->where('cart_id', $request->cart_id)->where('item_id', $request->item_id)->update(['count' => $newCount]);
            }
        } else {
            if ($request->count > 0) {
                DB::table('cart_items')->insert([
                    'cart_id' => $request->cart_id,
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

        $cartExists = DB::table('carts')->where('cart_id', $request->cart_id)->exists();
        if (!$cartExists) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $items = DB::table('cart_items')->where('cart_id', $request->cart_id)->get();
        return response()->json(['items' => $items], 200);
    }
}