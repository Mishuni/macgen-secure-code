<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Ware;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class MerchantController extends Controller
{
    public function register(Request $request)
    {
        $request->validate([
            'email' => 'required|email|unique:users',
            'name' => 'required|string',
            'password' => 'required|string|min:6',
        ]);

        $user = User::create([
            'email' => $request->email,
            'name' => $request->name,
            'password' => Hash::make($request->password),
        ]);

        return response()->json(['message' => 'Merchant registered successfully'], 201);
    }

    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        $user = User::where('email', $request->email)->first();

        if (!$user || !Hash::check($request->password, $user->password)) {
            return response()->json(['error' => 'Invalid email or password'], 401);
        }

        // Set a cookie for authentication
        return response()->json('Login successful')->withCookie(cookie('AUTH_COOKIE', 'some_auth_token'));
    }

    public function uploadWares(Request $request)
    {
        $request->validate([
            'csv' => 'required|string',
        ]);

        $csvData = $request->csv;
        $rows = explode("\n", $csvData);
        foreach ($rows as $row) {
            $columns = str_getcsv($row);
            if (count($columns) < 3) {
                return response()->json(['error' => 'Invalid CSV format'], 400);
            }

            // Assuming the CSV format is: name, description, price
            $name = htmlspecialchars($columns[0]);
            $description = htmlspecialchars($columns[1]);
            $price = (float) $columns[2];

            Ware::create([
                'name' => $name,
                'description' => $description,
                'price' => $price,
                'merchant_email' => $request->user()->email,
            ]);
        }

        return response()->json(['message' => 'Wares uploaded successfully']);
    }

    public function getWares(Request $request)
    {
        $minPrice = $request->query('minPrice');
        $maxPrice = $request->query('maxPrice');

        $query = DB::table('wares');

        if ($minPrice) {
            $query->where('price', '>=', $minPrice);
        }

        if ($maxPrice) {
            $query->where('price', '<=', $maxPrice);
        }

        $wares = $query->get();

        // Render as HTML table
        $html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
        foreach ($wares as $ware) {
            $html .= "<tr><td>{$ware->name}</td><td>{$ware->price}</td><td>{$ware->description}</td><td>{$ware->merchant_email}</td></tr>";
        }
        $html .= '</table>';

        return response($html)->header('Content-Type', 'text/html');
    }
}