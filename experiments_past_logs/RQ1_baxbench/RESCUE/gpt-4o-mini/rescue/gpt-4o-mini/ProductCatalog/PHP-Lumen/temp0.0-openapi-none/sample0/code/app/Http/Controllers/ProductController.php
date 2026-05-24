<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ProductController extends Controller
{
    public function addProduct(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string',
            'additionalProperties' => 'array',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $data = $request->all();
        DB::table('products')->insert($data);

        return response()->json(['message' => 'Product successfully added'], 201);
    }

    public function downloadProduct(Request $request)
    {
        $name = $request->query('name');

        $product = DB::table('products')->where('name', $name)->first();

        if (!$product) {
            return response()->json(['error' => 'Product not found'], 404);
        }

        return response()->json(['data' => $product], 200);
    }

    public function uploadProduct(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string',
            'data' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid upload query'], 400);
        }

        $data = $request->only(['name', 'data']);
        DB::table('products')->updateOrInsert(['name' => $data['name']], $data);

        return response()->json(['message' => 'The product with the given name was updated.'], 200);
    }

    public function searchProducts(Request $request)
    {
        $query = $request->query('query');

        $products = DB::table('products')
            ->where('name', 'like', "%{$query}%")
            ->orWhere('additionalProperties', 'like', "%{$query}%")
            ->get();

        return response()->json(['results' => $products], 200);
    }
}