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
        $this->validate($request, [
            'cart_id' => 'required|string',
            'item_id' => 'required|integer',
            'count' => 'required|integer',
        ]);

        $cartId = $request->input('cart_id');
        $itemId = $request->input('item_id');
        $count = $request->input('count');

        $cart = DB::table('carts')->where('cart_id', $cartId)->first();

        if (!$cart) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $item = DB::table('cart_items')->where('cart_id', $cartId)->where('item_id', $itemId)->first();

        if ($item) {
            $newCount = $item->count + $count;
            if ($newCount <= 0) {
                DB::table('cart_items')->where('cart_id', $cartId)->where('item_id', $itemId)->delete();
            } else {
                DB::table('cart_items')->where('cart_id', $cartId)->where('item_id', $itemId)->update(['count' => $newCount]);
            }
        } else {
            if ($count > 0) {
                DB::table('cart_items')->insert(['cart_id' => $cartId, 'item_id' => $itemId, 'count' => $count]);
            }
        }

        return response()->json(['message' => 'Item added or removed successfully'], 200);
    }

    public function retrieveCart(Request $request)
    {
        $this->validate($request, [
            'cart_id' => 'required|string',
        ]);

        $cartId = $request->input('cart_id');

        $cart = DB::table('carts')->where('cart_id', $cartId)->first();

        if (!$cart) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $items = DB::table('cart_items')->where('cart_id', $cartId)->get(['item_id', 'count']);

        return response()->json(['items' => $items], 200);
    }
}