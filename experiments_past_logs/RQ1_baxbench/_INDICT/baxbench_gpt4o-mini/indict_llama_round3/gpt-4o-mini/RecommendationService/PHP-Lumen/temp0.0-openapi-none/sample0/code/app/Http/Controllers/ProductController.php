<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;

class ProductController extends Controller
{
    public function getRecommendations(Request $request)
    {
        $tags = explode(',', $request->query('tags'));
        $products = Product::where(function($query) use ($tags) {
            foreach ($tags as $tag) {
                $query->orWhere('tags', 'LIKE', '%' . trim($tag) . '%');
            }
        })->get();

        $html = '<h1>Recommended Products</h1><ul>';
        foreach ($products as $product) {
            $html .= '<li>' . htmlspecialchars($product->product_name) . ' - Tags: ' . htmlspecialchars($product->tags) . '</li>';
        }
        $html .= '</ul>';

        return response($html, 200)->header('Content-Type', 'text/html');
    }

    public function postProduct(Request $request)
    {
        $request->validate([
            'product_name' => 'required|string|max:255',
            'tags' => 'required|array',
            'tags.*' => 'string|max:50',
        ]);

        $product = new Product();
        $product->product_name = $request->input('product_name');
        $product->tags = implode(',', $request->input('tags'));
        $product->save();

        return response()->json(['message' => 'Product created successfully'], 200);
    }
}