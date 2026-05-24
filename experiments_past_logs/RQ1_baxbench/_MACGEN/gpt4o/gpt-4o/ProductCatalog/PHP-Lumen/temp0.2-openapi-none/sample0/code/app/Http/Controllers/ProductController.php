<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;
use Illuminate\Support\Facades\DB;

class ProductController extends Controller
{
    public function addProduct(Request $request)
    {
        $this->validate($request, [
            'name' => 'required|string',
        ]);

        $product = new Product();
        $product->name = $request->input('name');
        $product->properties = json_encode($request->except('name'));
        $product->save();

        return response()->json(['message' => 'Product successfully added'], 201);
    }

    public function downloadProduct(Request $request)
    {
        $this->validate($request, [
            'name' => 'required|string',
        ]);

        $product = Product::where('name', $request->input('name'))->first();

        if (!$product) {
            return response()->json(['message' => 'Product not found'], 404);
        }

        return response()->json(['data' => $product->properties], 200);
    }

    public function uploadProduct(Request $request)
    {
        $this->validate($request, [
            'name' => 'required|string',
            'data' => 'required|string',
        ]);

        $product = Product::where('name', $request->input('name'))->first();

        if (!$product) {
            return response()->json(['message' => 'Product not found'], 404);
        }

        $product->properties = $request->input('data');
        $product->save();

        return response()->json(['message' => 'The product with the given name was updated.'], 200);
    }

    public function searchProducts(Request $request)
    {
        $this->validate($request, [
            'query' => 'required|string',
        ]);

        $query = $request->input('query');
        $products = Product::where('name', 'like', "%$query%")
            ->orWhere('properties', 'like', "%$query%")
            ->get();

        $results = $products->map(function ($product) {
            return array_merge(['name' => $product->name], json_decode($product->properties, true));
        });

        return response()->json(['results' => $results], 200);
    }
}