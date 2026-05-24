<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;

class MerchantController extends Controller
{
    public function register(Request $request)
    {
        $request->validate([
            'email' => 'required|email|unique:users,email',
            'name' => 'required|string',
            'password' => 'required|string|min:6',
        ]);

        $user = User::create([
            'email' => $request->email,
            'name' => $request->name,
            'password' => bcrypt($request->password),
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

        if (!$user || !password_verify($request->password, $user->password)) {
            return response()->json(['error' => 'Invalid email or password'], 401);
        }

        return response()->json('Login successful')->withCookie(cookie('AUTH_COOKIE', 'some_random_value')->httpOnly());
    }
}