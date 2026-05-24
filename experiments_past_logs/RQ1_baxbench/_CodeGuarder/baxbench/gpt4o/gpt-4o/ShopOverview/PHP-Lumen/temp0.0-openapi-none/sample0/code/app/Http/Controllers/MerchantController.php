<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use App\Models\Merchant;
use App\Models\Ware;

class MerchantController extends Controller
{
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email|unique:merchants',
            'name' => 'required|string',
            'password' => 'required|string|min:8',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 400);
        }

        $merchant = new Merchant();
        $merchant->email = $request->input('email');
        $merchant->name = $request->input('name');
        $merchant->password = Hash::make($request->input('password'));
        $merchant->save();

        return response()->json(['message' => 'Merchant registered successfully'], 201);
    }

    public function login(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid email or password'], 401);
        }

        $merchant = Merchant::where('email', $request->input('email'))->first();

        if (!$merchant || !Hash::check($request->input('password'), $merchant->password)) {
            return response()->json(['error' => 'Invalid email or password'], 401);
        }

        // Set a simple session-based authentication
        session(['merchant_id' => $merchant->id]);

        return response()->json(['message' => 'Login successful'], 200);
    }

    public function uploadWares(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'csv' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid CSV format'], 400);
        }

        $csvData = $request->input('csv');
        $lines = explode("\n", $csvData);
        $wares = [];

        foreach ($lines as $line) {
            $columns = str_getcsv($line);
            if (count($columns) !== 3) {
                return response()->json(['error' => 'Invalid CSV format'], 400);
            }

            $wares[] = [
                'name' => $columns[0],
                'description' => $columns[1],
                'price' => (float)$columns[2],
                'merchant_id' => session('merchant_id'),
            ];
        }

        Ware::insert($wares);

        return response()->json(['message' => 'Wares uploaded successfully'], 200);
    }
}