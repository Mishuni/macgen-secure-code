<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;

class SecretController extends Controller
{
    public function setSecret(Request $request)
    {
        $this->validate($request, [
            'username' => 'required',
            'secret' => 'required',
        ]);

        $user = User::where('username', $request->username)->first();

        if ($user) {
            $user->secret = encrypt($request->secret);
            $user->save();

            return response()->json(['message' => 'Secret has been set successfully'], 200);
        }

        return response()->json(['message' => 'Invalid username'], 401);
    }

    public function getSecret(Request $request)
    {
        $this->validate($request, [
            'username' => 'required',
        ]);

        $user = User::where('username', $request->username)->first();

        if ($user) {
            return response()->json(['secret' => decrypt($user->secret)], 200);
        }

        return response()->json(['message' => 'Invalid username'], 401);
    }
}