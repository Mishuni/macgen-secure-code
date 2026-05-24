<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;
use App\Models\Tag;

class ProductController extends Controller
{
    public function getProductsByTags(Request $request)
    {
        $tags = array_map('trim', explode(',', $request->query('tags', '')));
        $tags = array_filter($tags, function($tag) {
            return !empty($tag);
        });

        if (empty($tags)) {
            return response('<p>No tags provided.</p>', 400)->header('Content-Type', 'text/html');
        }

        $products = Product::whereHas('tags', function ($query) use ($tags) {
            $query->whereIn('name', $tags);
        })->get();

        $html = '<ul>';
        foreach ($products as $product) {
            $html .= '<li>' . htmlspecialchars($product->name, ENT_QUOTES, 'UTF-8') . '</li>';
        }
        $html .= '</ul>';

        return response($html, 200)->header('Content-Type', 'text/html');
    }

    public function postProduct(Request $request)
    {
        $this->validate($request, [
            'product_name' => 'required|string|max:255',
            'tags' => 'required|array',
            'tags.*' => 'string|max:50',
        ]);

        $product = new Product();
        $product->name = $request->input('product_name');
        $product->save();

        $tags = array_map('trim', $request->input('tags'));
        $tags = array_filter($tags, function($tag) {
            return !empty($tag);
        });

        $product->tags()->createMany(array_map(function ($tag) {
            return ['name' => $tag];
        }, $tags));

        return response()->json(['message' => 'Product created successfully'], 200);
    }
}