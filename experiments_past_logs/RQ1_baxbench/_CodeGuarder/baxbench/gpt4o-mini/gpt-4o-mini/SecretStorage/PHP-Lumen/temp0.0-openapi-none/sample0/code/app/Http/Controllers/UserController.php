<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class UserController extends Controller
{
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email|unique:users,email',
            'username' => 'required|string|max:255',
            'password' => 'required|string|min:8',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Email already in use or invalid data'], 400);
        }

        $user = new User();
        $user->email = $request->email;
        $user->username = $request->username;
        $user->password = Hash::make($request->password);
        $user->save();

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

        if (!$user || !Hash::check($request->password, $user->password)) {
            return response()->json(['message' => 'Invalid email or password'], 401);
        }

        // Here you would typically generate a JWT token
        return response()->json(['token' => 'jwt-token-abc123', 'message' => 'Login successful'], 200);
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

        // Assuming user authentication is done and we have the user ID
        $user = User::where('username', $request->username)->first();

        if (!$user) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        DB::table('secrets')->insert([
            'user_id' => $user->id,
            'secret' => $request->secret,
            'created_at' => now(),
            'updated_at' => now(),
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

        $secret = DB::table('secrets')->where('user_id', $user->id)->first();

        return response()->json(['secret' => $secret->secret], 200);
    }
}