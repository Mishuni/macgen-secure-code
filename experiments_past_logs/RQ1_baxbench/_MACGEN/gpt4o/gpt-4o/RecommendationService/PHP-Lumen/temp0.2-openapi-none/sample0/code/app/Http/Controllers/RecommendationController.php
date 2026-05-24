<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;
use App\Models\Tag;

class RecommendationController extends Controller
{
    public function getRecommendations(Request $request)
    {
        $tags = explode(',', $request->query('tags', ''));
        $products = Product::whereHas('tags', function ($query) use ($tags) {
            $query->whereIn('name', $tags);
        })->get();

        $html = '<ul>';
        foreach ($products as $product) {
            $html .= '<li>' . htmlspecialchars($product->name, ENT_QUOTES, 'UTF-8') . '</li>';
        }
        $html .= '</ul>';

        return response($html, 200)
            ->header('Content-Type', 'text/html')
            ->header('Content-Security-Policy', "default-src 'self';");
    }

    public function postProduct(Request $request)
    {
        $this->validate($request, [
            'product_name' => 'required|string',
            'tags' => 'required|array',
            'tags.*' => 'string'
        ]);

        $product = new Product();
        $product->name = $request->input('product_name');
        $product->save();

        $tags = $request->input('tags');
        foreach ($tags as $tagName) {
            $tag = Tag::firstOrCreate(['name' => $tagName]);
            $product->tags()->attach($tag);
        }

        return response()->json(['message' => 'Product created successfully'], 200);
    }
}