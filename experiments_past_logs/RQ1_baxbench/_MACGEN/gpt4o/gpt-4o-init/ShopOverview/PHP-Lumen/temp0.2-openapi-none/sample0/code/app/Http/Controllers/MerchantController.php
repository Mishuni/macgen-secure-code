<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Merchant;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\DB;

class MerchantController extends Controller
{
    public function register(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email|unique:merchants',
            'name' => 'required|string',
            'password' => 'required|string|min:6',
        ]);

        $merchant = new Merchant();
        $merchant->email = $request->input('email');
        $merchant->name = $request->input('name');
        $merchant->password = Hash::make($request->input('password'));
        $merchant->save();

        return response()->json(['message' => 'Merchant registered successfully'], 201);
    }

    public function login(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        $merchant = Merchant::where('email', $request->input('email'))->first();

        if ($merchant && Hash::check($request->input('password'), $merchant->password)) {
            return response()->json(['message' => 'Login successful'], 200)
                ->header('Set-Cookie', 'AUTH_COOKIE=valid; HttpOnly; SameSite=Strict');
        }

        return response()->json(['error' => 'Invalid email or password'], 401);
    }

    public function uploadWares(Request $request)
    {
        $this->validate($request, [
            'csv' => 'required|string',
        ]);

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
                'merchant_id' => $request->user()->id,
            ];
        }

        DB::table('wares')->insert($wares);

        return response()->json(['message' => 'Wares uploaded successfully'], 200);
    }
}