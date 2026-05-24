<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;

class ProductController extends Controller
{
    public function add(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:255',
            'additionalProperties' => 'array',
            'additionalProperties.*' => 'string|max:255', // Updated validation rule
        ]);

        $product = new Product();
        $product->name = $request->name;
        $product->additionalProperties = json_encode($request->additionalProperties);
        $product->save();

        return response()->json(['message' => 'Product successfully added'], 201);
    }

    public function download(Request $request)
    {
        $request->validate(['name' => 'required|string|max:255']);
        $product = Product::where('name', $request->name)->first();

        if (!$product) {
            return response()->json(['message' => 'Product not found'], 404);
        }

        return response()->json(['data' => $product], 200);
    }

    public function upload(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:255',
            'data' => 'required|string',
        ]);

        $data = json_decode($request->data, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return response()->json(['message' => 'Invalid data format'], 400);
        }

        $product = Product::updateOrCreate(['name' => $request->name], $data);
        return response()->json(['message' => 'Product updated'], 200);
    }

    public function search(Request $request)
    {
        $request->validate(['query' => 'required|string|max:255']);
        $products = Product::where('name', 'like', '%' . $request->query . '%')->get();

        return response()->json(['results' => $products], 200);
    }
}