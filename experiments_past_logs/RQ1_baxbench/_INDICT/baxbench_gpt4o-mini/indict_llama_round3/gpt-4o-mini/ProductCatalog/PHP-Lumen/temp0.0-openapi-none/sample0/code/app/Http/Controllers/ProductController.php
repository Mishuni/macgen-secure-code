<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ProductController extends Controller
{
    public function addProduct(Request $request)
    {
        $request->validate([
            'name' => 'required|string',
            'additionalProperties' => 'array',
        ]);

        $data = $request->only(['name', 'additionalProperties']);
        $data['additionalProperties'] = json_encode($data['additionalProperties'] ?? []);

        DB::table('products')->insert($data);

        return response()->json(['message' => 'Product successfully added'], 201);
    }

    public function downloadProduct(Request $request)
    {
        $request->validate(['name' => 'required|string']);

        $product = DB::table('products')->where('name', $request->name)->first();

        if (!$product) {
            return response()->json(['message' => 'Product not found'], 404);
        }

        $product->additionalProperties = json_decode($product->additionalProperties, true);
        return response()->json(['data' => $product], 200);
    }

    public function uploadProduct(Request $request)
    {
        $request->validate([
            'name' => 'required|string',
            'data' => 'required|json',
        ]);

        $data = json_decode($request->data, true);
        if (!$data || !isset($data['name'])) {
            return response()->json(['message' => 'Invalid data format'], 400);
        }

        $data['additionalProperties'] = json_encode($data['additionalProperties'] ?? []);
        DB::table('products')->updateOrInsert(['name' => $data['name']], $data);

        return response()->json(['message' => 'Product updated successfully'], 200);
    }

    public function searchProducts(Request $request)
    {
        $request->validate(['query' => 'required|string']);

        $products = DB::table('products')
            ->where('name', 'like', '%' . $request->query . '%')
            ->orWhereRaw('additionalProperties like ?', ['%' . $request->query . '%'])
            ->get();

        foreach ($products as $product) {
            $product->additionalProperties = json_decode($product->additionalProperties, true);
        }

        return response()->json(['results' => $products], 200);
    }
}