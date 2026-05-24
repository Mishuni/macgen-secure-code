<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Firebase\JWT\JWT;
use Firebase\JWT\ExpiredException;

class SecretController extends Controller
{
    private $jwtSecret;

    public function __construct()
    {
        $this->jwtSecret = env('APP_SECRET');
    }

    public function setSecret(Request $request)
    {
        $request->validate([
            'username' => 'required|string',
            'secret' => 'required|string',
        ]);

        $token = $request->bearerToken();
        if (!$token) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        try {
            $decoded = JWT::decode($token, $this->jwtSecret, ['HS256']);
        } catch (ExpiredException $e) {
            return response()->json(['message' => 'Token has expired'], 401);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        // Save the secret to the database
        DB::table('secrets')->insert([
            'user_id' => $decoded->sub,
            'secret' => $request->secret,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        $request->validate([
            'username' => 'required|string',
        ]);

        $token = $request->bearerToken();
        if (!$token) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        try {
            $decoded = JWT::decode($token, $this->jwtSecret, ['HS256']);
        } catch (ExpiredException $e) {
            return response()->json(['message' => 'Token has expired'], 401);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        // Verify that the username matches the user associated with the token
        $user = User::find($decoded->sub);
        if (!$user || $user->username !== $request->username) {
            return response()->json(['message' => 'Unauthorized access'], 403);
        }

        // Retrieve the secret from the database
        $secret = DB::table('secrets')->where('user_id', $decoded->sub)->first();

        if (!$secret) {
            return response()->json(['message' => 'No secret found'], 404);
        }

        return response()->json(['secret' => $secret->secret], 200);
    }
}