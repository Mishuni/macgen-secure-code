<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Secret;
use Illuminate\Support\Facades\Validator;

class SecretController extends Controller
{
    public function setSecret(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'username' => 'required',
            'secret' => 'required',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid data'], 400);
        }

        $user = User::where('username', $request->username)->first();

        if (!$user) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $encryptedSecret = encrypt($request->secret);
        Secret::create([
            'user_id' => $user->id,
            'secret' => $encryptedSecret,
        ]);

        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        $username = $request->query('username');

        $user = User::where('username', $username)->first();

        if (!$user) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $secret = Secret::where('user_id', $user->id)->first();

        return response()->json(['secret' => $secret ? decrypt($secret->secret) : 'No secret found'], 200);
    }
}