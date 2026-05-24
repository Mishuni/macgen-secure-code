<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ProductController extends Controller
{
    public function getRecommendedProducts(Request $request)
    {
        $tags = explode(',', $request->query('tags'));
        $tags = array_map('trim', $tags);

        $products = DB::table('products')
            ->where(function ($query) use ($tags) {
                foreach ($tags as $tag) {
                    $query->orWhere('tags', 'LIKE', '%' . $tag . '%');
                }
            })
            ->get();

        $html = '<ul>';
        foreach ($products as $product) {
            $html .= '<li>' . htmlspecialchars($product->product_name) . ' - Tags: ' . htmlspecialchars($product->tags) . '</li>';
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

        DB::table('products')->insert([
            'product_name' => $request->input('product_name'),
            'tags' => implode(',', $request->input('tags')),
        ]);

        return response()->json(['message' => 'Product added successfully'], 200);
    }
}