<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class RecommendationController extends Controller
{
    /**
     * Get all products that match at least one of the provided tags.
     */
    public function getRecommendations(Request $request)
    {
        $tags = $request->query('tags');

        if (!$tags) {
            return response('Tags parameter is required.', 400);
        }

        $tagsArray = explode(',', $tags);

        // Use parameterized query to prevent SQL injection
        $placeholders = implode(',', array_fill(0, count($tagsArray), '?'));
        $query = "SELECT product_name, tags FROM products WHERE tags LIKE ?";
        $params = array_map(fn($tag) => "%$tag%", $tagsArray);

        $products = DB::select("SELECT product_name, tags FROM products WHERE " . implode(' OR ', array_fill(0, count($tagsArray), "tags LIKE ?")), $params);

        $html = '<ul>';
        foreach ($products as $product) {
            $html .= '<li>' . htmlspecialchars($product->product_name) . ' - Tags: ' . htmlspecialchars($product->tags) . '</li>';
        }
        $html .= '</ul>';

        return response($html, 200)->header('Content-Type', 'text/html');
    }

    /**
     * Post a new product along with its tags.
     */
    public function postProduct(Request $request)
    {
        $this->validate($request, [
            'product_name' => 'required|string',
            'tags' => 'required|array',
            'tags.*' => 'string',
        ]);

        $productName = $request->input('product_name');
        $tags = implode(',', $request->input('tags'));

        // Use parameterized query to prevent SQL injection
        DB::insert('INSERT INTO products (product_name, tags) VALUES (?, ?)', [$productName, $tags]);

        return response('Product added successfully.', 200);
    }
}