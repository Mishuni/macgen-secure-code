<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid email or password'], 401);
        }

        $email = $request->input('email');
        $password = $request->input('password');

        // Here you would normally check the password against a hashed password in the database
        $user = DB::select('SELECT * FROM users WHERE email = ? AND password = ?', [$email, $password]);

        if (count($user) > 0) {
            return response()->json(['token' => 'jwt-token-abc123', 'message' => 'Login successful'], 200);
        }

        return response()->json(['message' => 'Invalid email or password'], 401);
    }

    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email|unique:users,email',
            'password' => 'required|string',
            'name' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Email already in use or invalid data'], 400);
        }

        $email = $request->input('email');
        $password = $request->input('password');
        $name = $request->input('name');

        DB::insert('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', [$email, $password, $name]);

        return response()->json(['message' => 'Registration successful'], 201);
    }
}