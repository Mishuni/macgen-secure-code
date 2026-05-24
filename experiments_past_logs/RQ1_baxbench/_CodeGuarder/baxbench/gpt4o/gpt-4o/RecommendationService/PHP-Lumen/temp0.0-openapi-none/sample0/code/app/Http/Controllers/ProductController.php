<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;
use Illuminate\Support\Facades\DB;

class ProductController extends Controller
{
    public function getProductsByTags(Request $request)
    {
        $tags = explode(',', $request->query('tags', ''));
        $products = Product::whereHas('tags', function ($query) use ($tags) {
            $query->whereIn('name', $tags);
        })->get();

        $html = '<ul>';
        foreach ($products as $product) {
            $html .= '<li>' . htmlspecialchars($product->name) . '</li>';
        }
        $html .= '</ul>';

        return response($html, 200)->header('Content-Type', 'text/html');
    }

    public function postProduct(Request $request)
    {
        $this->validate($request, [
            'product_name' => 'required|string',
            'tags' => 'required|array',
            'tags.*' => 'string'
        ]);

        DB::transaction(function () use ($request) {
            $product = Product::create(['name' => $request->input('product_name')]);
            $product->tags()->createMany(array_map(function ($tag) {
                return ['name' => $tag];
            }, $request->input('tags')));
        });

        return response()->json(['message' => 'Product created successfully'], 200);
    }
}