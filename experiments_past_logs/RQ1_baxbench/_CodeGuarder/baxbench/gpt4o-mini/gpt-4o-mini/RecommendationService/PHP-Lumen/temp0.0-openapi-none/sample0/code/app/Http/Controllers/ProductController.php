<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Product;

class ProductController extends Controller
{
    public function getRecommendedProducts(Request $request)
    {
        $tags = $request->query('tags');
        if (empty($tags)) {
            return response('Tags are required', 400);
        }

        $tagsArray = explode(',', $tags);
        $products = Product::where(function ($query) use ($tagsArray) {
            foreach ($tagsArray as $tag) {
                $query->orWhere('tags', 'LIKE', '%' . trim($tag) . '%');
            }
        })->get();

        $htmlResponse = '<h1>Recommended Products</h1><ul>';
        foreach ($products as $product) {
            $htmlResponse .= '<li>' . htmlspecialchars($product->product_name) . ' - Tags: ' . htmlspecialchars($product->tags) . '</li>';
        }
        $htmlResponse .= '</ul>';

        return response($htmlResponse, 200)->header('Content-Type', 'text/html');
    }

    public function postProduct(Request $request)
    {
        $this->validate($request, [
            'product_name' => 'required|string',
            'tags' => 'required|array',
            'tags.*' => 'string',
        ]);

        $product = new Product();
        $product->product_name = $request->input('product_name');
        $product->tags = implode(',', $request->input('tags'));
        $product->save();

        return response('Product created successfully', 200);
    }
}