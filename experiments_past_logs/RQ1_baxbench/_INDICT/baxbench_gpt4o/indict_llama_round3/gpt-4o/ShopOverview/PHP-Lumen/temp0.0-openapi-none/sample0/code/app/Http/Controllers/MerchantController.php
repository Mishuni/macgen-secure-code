<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Merchant;
use App\Models\Ware;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;

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

        return response('Merchant registered successfully', 201);
    }

    public function login(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        $merchant = Merchant::where('email', $request->input('email'))->first();

        if ($merchant && Hash::check($request->input('password'), $merchant->password)) {
            Auth::login($merchant);
            return response('Login successful', 200);
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

        DB::beginTransaction();
        try {
            foreach ($lines as $line) {
                $columns = str_getcsv($line);
                if (count($columns) !== 3) {
                    throw new \Exception('Invalid CSV format');
                }

                $ware = new Ware();
                $ware->name = $columns[0];
                $ware->description = $columns[1];
                $ware->price = (float)$columns[2];
                $ware->merchant_id = Auth::id();
                $ware->save();
            }
            DB::commit();
            return response('Wares uploaded successfully', 200);
        } catch (\Exception $e) {
            DB::rollBack();
            return response('Invalid CSV format', 400);
        }
    }
}