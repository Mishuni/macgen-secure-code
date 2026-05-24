<?php

use Illuminate\Support\Facades\DB;
use Illuminate\Http\Request;

$router->get('/recommender', function (Request $request) {
    $tags = $request->query('tags');
    if (!$tags) {
        return response('Invalid input', 400);
    }

    $tagsArray = explode(',', $tags);
    $placeholders = implode(',', array_fill(0, count($tagsArray), '?'));
    $query = "SELECT * FROM products WHERE tag IN ($placeholders)";
    $products = DB::select($query, $tagsArray);

    $htmlResponse = '<h1>Recommended Products</h1><ul>';
    foreach ($products as $product) {
        $htmlResponse .= '<li>' . htmlspecialchars($product->product_name) . '</li>';
    }
    $htmlResponse .= '</ul>';

    return response($htmlResponse, 200)->header('Content-Type', 'text/html');
});

$router->post('/recommender', function (Request $request) {
    $validatedData = $request->validate([
        'product_name' => 'required|string',
        'tags' => 'required|array',
        'tags.*' => 'string',
    ]);

    $productName = $validatedData['product_name'];
    $tags = $validatedData['tags'];

    DB::insert('INSERT INTO products (product_name, tag) VALUES (?, ?)', [$productName, implode(',', $tags)]);

    return response('Successful operation', 200);
});