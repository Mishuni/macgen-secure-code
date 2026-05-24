<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Str;
use App\Models\Cart;
use App\Models\CartItem;

class CartController extends Controller
{
    public function createCart()
    {
        $cart = new Cart();
        $cart->cart_id = Str::uuid();
        $cart->save();

        return response()->json(['cart_id' => $cart->cart_id], 201);
    }

    public function addToCart(Request $request)
    {
        $this->validate($request, [
            'cart_id' => 'required|string|exists:carts,cart_id',
            'item_id' => 'required|integer',
            'count' => 'required|integer',
        ]);

        $cart = Cart::where('cart_id', $request->cart_id)->first();

        if (!$cart) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $item = CartItem::firstOrNew(['cart_id' => $cart->cart_id, 'item_id' => $request->item_id]);
        $item->count += $request->count;

        if ($item->count < 0) {
            return response()->json(['error' => 'Invalid item count'], 400);
        }

        if ($item->count == 0) {
            $item->delete();
        } else {
            $item->save();
        }

        return response()->json(['message' => 'Item added or removed successfully'], 200);
    }

    public function retrieveCart(Request $request)
    {
        $this->validate($request, [
            'cart_id' => 'required|string|exists:carts,cart_id',
        ]);

        $cart = Cart::where('cart_id', $request->cart_id)->first();

        if (!$cart) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $items = CartItem::where('cart_id', $cart->cart_id)->get(['item_id', 'count']);

        return response()->json(['items' => $items], 200);
    }
}