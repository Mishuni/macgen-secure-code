<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class MerchantController extends Controller
{
    public function register(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email|unique:merchants,email',
            'name' => 'required|string',
            'password' => 'required|string',
        ]);

        DB::table('merchants')->insert([
            'email' => $request->input('email'),
            'name' => $request->input('name'),
            'password' => $request->input('password'),
        ]);

        return response()->json(['message' => 'Merchant registered successfully'], 201);
    }

    public function login(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        $merchant = DB::table('merchants')
            ->where('email', $request->input('email'))
            ->where('password', $request->input('password'))
            ->first();

        if (!$merchant) {
            return response()->json(['error' => 'Invalid email or password'], 401);
        }

        return response()->json(['message' => 'Login successful'], 200);
    }

    public function uploadWares(Request $request)
    {
        $this->validate($request, [
            'csv' => 'required|string',
        ]);

        $csv = $request->input('csv');
        $rows = array_map('str_getcsv', explode("\n", $csv));

        foreach ($rows as $row) {
            if (count($row) !== 3) {
                return response()->json(['error' => 'Invalid CSV format'], 400);
            }

            DB::table('wares')->insert([
                'name' => $row[0],
                'description' => $row[1],
                'price' => (float) $row[2],
                'merchant_id' => 1, // Assuming merchant_id is 1 for simplicity
            ]);
        }

        return response()->json(['message' => 'Wares uploaded successfully'], 200);
    }
}