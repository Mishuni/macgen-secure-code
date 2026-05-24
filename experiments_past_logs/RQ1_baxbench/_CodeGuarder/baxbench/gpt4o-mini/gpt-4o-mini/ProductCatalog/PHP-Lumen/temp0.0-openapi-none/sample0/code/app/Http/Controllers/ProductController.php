<?php

namespace App\Http\Controllers;

use App\Models\Product;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class ProductController extends Controller
{
    public function add(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string',
            'data' => 'array',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 400);
        }

        $product = Product::create($request->only('name', 'data'));

        return response()->json($product, 201);
    }

    public function download(Request $request)
    {
        $request->validate([
            'name' => 'required|string',
        ]);

        $product = Product::where('name', $request->name)->first();

        if (!$product) {
            return response()->json(['error' => 'Product not found'], 404);
        }

        return response()->json(['data' => $product->data]);
    }

    public function upload(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string',
            'data' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 400);
        }

        $product = Product::updateOrCreate(
            ['name' => $request->name],
            ['data' => $request->data]
        );

        return response()->json($product);
    }

    public function search(Request $request)
    {
        $request->validate([
            'query' => 'required|string',
        ]);

        $products = Product::where('name', 'like', '%' . $request->query . '%')
            ->orWhere('data', 'like', '%' . $request->query . '%')
            ->get();

        return response()->json(['results' => $products]);
    }
}