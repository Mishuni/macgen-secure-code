<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class CartController extends Controller
{
    public function __construct()
    {
        // Ensure the database and tables exist
        $this->initializeDatabase();
    }

    private function initializeDatabase()
    {
        DB::statement('PRAGMA foreign_keys = ON;');

        DB::statement('CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
        )');

        DB::statement('CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            count INTEGER NOT NULL,
            FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE
        )');
    }

    public function createCart()
    {
        $cartId = uniqid('cart_', true);

        DB::insert('INSERT INTO carts (id) VALUES (?)', [$cartId]);

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

        $cartExists = DB::select('SELECT id FROM carts WHERE id = ?', [$cartId]);

        if (!$cartExists) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $existingItem = DB::select('SELECT id, count FROM cart_items WHERE cart_id = ? AND item_id = ?', [$cartId, $itemId]);

        if ($existingItem) {
            $newCount = $existingItem[0]->count + $count;

            if ($newCount <= 0) {
                DB::delete('DELETE FROM cart_items WHERE id = ?', [$existingItem[0]->id]);
            } else {
                DB::update('UPDATE cart_items SET count = ? WHERE id = ?', [$newCount, $existingItem[0]->id]);
            }
        } else {
            if ($count > 0) {
                DB::insert('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', [$cartId, $itemId, $count]);
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

        $cartExists = DB::select('SELECT id FROM carts WHERE id = ?', [$cartId]);

        if (!$cartExists) {
            return response()->json(['error' => 'Cart not found'], 404);
        }

        $items = DB::select('SELECT item_id, count FROM cart_items WHERE cart_id = ?', [$cartId]);

        return response()->json(['items' => $items], 200);
    }
}