<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class UserController extends Controller
{
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email|unique:users,email',
            'username' => 'required|string|unique:users,username',
            'password' => 'required|string|min:6',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Email already in use or invalid data'], 400);
        }

        $user = User::create([
            'email' => $request->email,
            'username' => $request->username,
            'password' => $request->password, // Note: Password should be hashed in production
        ]);

        return response()->json(['message' => 'Registration successful'], 201);
    }

    public function login(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid email or password'], 401);
        }

        $user = User::where('email', $request->email)->first();

        if (!$user || $user->password !== $request->password) { // Note: Password comparison should be done with hashed passwords
            return response()->json(['message' => 'Invalid email or password'], 401);
        }

        // Generate a token (not implemented in this example)
        $token = 'jwt-token-abc123'; // Placeholder for JWT token generation

        return response()->json(['token' => $token, 'message' => 'Login successful'], 200);
    }

    public function setSecret(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'username' => 'required|string',
            'secret' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid data'], 400);
        }

        // Here you would save the secret associated with the username
        // This is a placeholder response
        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        $username = $request->query('username');

        if (!$username) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        // Here you would retrieve the secret associated with the username
        // This is a placeholder response
        return response()->json(['secret' => 'The secret associated with the provided details'], 200);
    }
}