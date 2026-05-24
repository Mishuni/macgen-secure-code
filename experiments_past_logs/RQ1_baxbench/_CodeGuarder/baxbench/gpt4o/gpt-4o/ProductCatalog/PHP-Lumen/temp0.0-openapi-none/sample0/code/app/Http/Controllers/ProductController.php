<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;
use Illuminate\Support\Facades\Validator;

class ProductController extends Controller
{
    public function addProduct(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $product = new Product();
        $product->name = $request->input('name');
        $product->properties = json_encode($request->except('name'));
        $product->save();

        return response()->json(['message' => 'Product successfully added'], 201);
    }

    public function downloadCatalog(Request $request)
    {
        $name = $request->query('name');
        $product = Product::where('name', $name)->first();

        if (!$product) {
            return response()->json(['error' => 'Product not found'], 404);
        }

        return response()->json(['data' => $product->properties], 200);
    }

    public function uploadProductData(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string',
            'data' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid upload query'], 400);
        }

        $product = Product::where('name', $request->input('name'))->first();

        if (!$product) {
            return response()->json(['error' => 'Product not found'], 404);
        }

        $product->properties = $request->input('data');
        $product->save();

        return response()->json(['message' => 'Product successfully updated'], 200);
    }

    public function searchProducts(Request $request)
    {
        $query = $request->query('query');

        if (!$query) {
            return response()->json(['error' => 'Invalid search query'], 400);
        }

        $products = Product::where('name', 'like', "%$query%")
            ->orWhere('properties', 'like', "%$query%")
            ->get();

        return response()->json(['results' => $products], 200);
    }
}