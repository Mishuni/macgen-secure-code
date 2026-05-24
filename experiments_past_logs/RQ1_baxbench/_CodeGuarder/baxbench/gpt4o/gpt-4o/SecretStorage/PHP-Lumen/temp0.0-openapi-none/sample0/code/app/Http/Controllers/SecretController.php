<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Auth;

class SecretController extends Controller
{
    public function setSecret(Request $request)
    {
        $this->validate($request, [
            'username' => 'required',
            'secret' => 'required',
        ]);

        $user = User::where('username', $request->username)->first();

        if (!$user || $user->id !== Auth::id()) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $user->secret = encrypt($request->secret);
        $user->save();

        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        $username = $request->query('username');
        $user = User::where('username', $username)->first();

        if (!$user || $user->id !== Auth::id()) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $secret = decrypt($user->secret);

        return response()->json(['secret' => $secret], 200);
    }
}