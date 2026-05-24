<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ProductController extends Controller
{
    public function __construct()
    {
        // Ensure the database table exists
        DB::statement('CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )');
    }

    public function addProduct(Request $request)
    {
        $this->validate($request, [
            'name' => 'required|string',
        ]);

        $name = $request->input('name');
        $data = json_encode($request->except('name'));

        try {
            DB::insert('INSERT INTO products (name, data) VALUES (?, ?)', [$name, $data]);
            return response()->json(['message' => 'Product successfully added'], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input or product already exists'], 400);
        }
    }

    public function downloadCatalog(Request $request)
    {
        $this->validate($request, [
            'name' => 'required|string',
        ]);

        $name = $request->input('name');

        $product = DB::select('SELECT data FROM products WHERE name = ?', [$name]);

        if (empty($product)) {
            return response()->json(['error' => 'Product not found'], 400);
        }

        return response()->json(['data' => $product[0]->data], 200);
    }

    public function uploadCatalog(Request $request)
    {
        $this->validate($request, [
            'name' => 'required|string',
            'data' => 'required|string',
        ]);

        $name = $request->input('name');
        $data = $request->input('data');

        try {
            $updated = DB::update('UPDATE products SET data = ? WHERE name = ?', [$data, $name]);

            if ($updated === 0) {
                return response()->json(['error' => 'Product not found'], 400);
            }

            return response()->json(['message' => 'Product successfully updated'], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid upload query'], 400);
        }
    }

    public function searchProducts(Request $request)
    {
        $this->validate($request, [
            'query' => 'required|string',
        ]);

        $query = $request->input('query');
        $query = '%' . $query . '%';

        $products = DB::select('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [$query, $query]);

        $results = array_map(function ($product) {
            $data = json_decode($product->data, true);
            $data['name'] = $product->name;
            return $data;
        }, $products);

        return response()->json(['results' => $results], 200);
    }
}