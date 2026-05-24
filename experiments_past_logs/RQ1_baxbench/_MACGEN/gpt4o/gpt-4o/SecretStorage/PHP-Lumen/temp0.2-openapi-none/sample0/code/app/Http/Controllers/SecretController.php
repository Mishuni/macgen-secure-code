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

        if (!$user || $user->api_token !== $request->bearerToken()) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $encryptedSecret = encrypt($request->secret);

        Secret::updateOrCreate(
            ['user_id' => $user->id],
            ['secret' => $encryptedSecret]
        );

        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        $username = $request->query('username');
        $user = User::where('username', $username)->first();

        if (!$user || $user->api_token !== $request->bearerToken()) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $secret = Secret::where('user_id', $user->id)->first();

        if ($secret) {
            $decryptedSecret = decrypt($secret->secret);
            return response()->json(['secret' => $decryptedSecret], 200);
        }

        return response()->json(['message' => 'No secret found'], 404);
    }
}