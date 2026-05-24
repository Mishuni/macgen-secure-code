<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
            'password' => 'required'
        ]);

        $user = User::where('email', $request->email)->first();

        if ($user && Hash::check($request->password, $user->password)) {
            $payload = [
                'iss' => "lumen-jwt", // Issuer of the token
                'sub' => $user->id, // Subject of the token
                'iat' => time(), // Time when JWT was issued
                'exp' => time() + 60*60 // Expiration time
            ];

            $token = JWT::encode($payload, env('APP_SECRET'), 'HS256');

            return response()->json([
                'token' => $token,
                'message' => 'Login successful'
            ], 200);
        }

        return response()->json(['message' => 'Invalid email or password'], 401);
    }

    public function register(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email|unique:users',
            'password' => 'required',
            'name' => 'required'
        ]);

        $user = User::create([
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'name' => $request->name
        ]);

        return response()->json(['message' => 'Registration successful'], 201);
    }
}