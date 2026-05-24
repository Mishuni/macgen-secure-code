<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class MerchantController extends Controller
{
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'name' => 'required|string',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        DB::table('merchants')->insert([
            'email' => $request->email,
            'name' => $request->name,
            'password' => $request->password, // Note: In production, hash the password
        ]);

        return response()->json(['message' => 'Merchant registered successfully'], 201);
    }

    public function login(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $merchant = DB::table('merchants')->where('email', $request->email)->first();

        if (!$merchant || $merchant->password !== $request->password) { // Note: In production, verify hashed password
            return response()->json(['error' => 'Invalid email or password'], 401);
        }

        // Set cookie for session (not implemented here)
        return response()->json(['message' => 'Login successful']);
    }

    public function uploadWares(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'csv' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid CSV format'], 400);
        }

        // Process CSV and insert into database
        // This is a placeholder for actual CSV processing logic
        // Example: parse CSV and insert into 'wares' table

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

        // Render as HTML table (placeholder)
        return response()->view('wares.index', ['wares' => $wares]);
    }
}