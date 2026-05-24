<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ProductController extends Controller
{
    public function add(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $data = $request->except(['name']);
        $productData = json_encode($data);

        try {
            DB::table('products')->insert(['name' => $request->name, 'data' => $productData]);
            return response()->json(['message' => 'Product successfully added'], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to add product'], 500);
        }
    }

    public function download(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        try {
            $product = DB::table('products')->where('name', $request->name)->first();

            if ($product) {
                return response()->json(['data' => $product->data], 200);
            }

            return response()->json(['error' => 'Product not found'], 404);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to retrieve product'], 500);
        }
    }

    public function upload(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'data' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        try {
            $updated = DB::table('products')->where('name', $request->name)->update(['data' => $request->data]);

            if ($updated) {
                return response()->json(['message' => 'The product with the given name was updated.'], 200);
            }

            return response()->json(['error' => 'Product not found'], 404);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to update product'], 500);
        }
    }

    public function search(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'query' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        try {
            $query = $request->query;
            $results = DB::table('products')
                ->where('name', 'like', '%' . $query . '%')
                ->orWhere('data', 'like', '%' . $query . '%')
                ->get()
                ->map(function ($product) {
                    $productData = json_decode($product->data, true);
                    $productData['name'] = $product->name;
                    return $productData;
                });

            return response()->json(['results' => $results], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to search products'], 500);
        }
    }
}