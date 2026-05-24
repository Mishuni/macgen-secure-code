<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Models\User;

class AuthController extends Controller
{
    public function register(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email|unique:users,email',
            'password' => 'required|min:8',
            'name' => 'required|string|max:255',
        ]);

        // Insert user into the database
        DB::table('users')->insert([
            'email' => $request->input('email'),
            'password' => $request->input('password'),
            'name' => $request->input('name'),
        ]);

        return response()->json(['message' => 'Registration successful'], 201);
    }

    public function login(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
            'password' => 'required',
        ]);

        $user = DB::table('users')
            ->where('email', $request->input('email'))
            ->where('password', $request->input('password'))
            ->first();

        if ($user) {
            return response()->json([
                'token' => 'jwt-token-abc123',
                'message' => 'Login successful',
            ], 200);
        }

        return response()->json(['message' => 'Invalid email or password'], 401);
    }
}