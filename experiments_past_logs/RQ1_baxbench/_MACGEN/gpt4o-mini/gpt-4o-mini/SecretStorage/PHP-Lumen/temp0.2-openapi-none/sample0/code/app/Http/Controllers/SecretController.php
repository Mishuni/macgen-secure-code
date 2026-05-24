<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Secret;
use Illuminate\Support\Facades\Validator;
use Firebase\JWT\JWT;
use Firebase\JWT\ExpiredException;

class SecretController extends Controller
{
    public function setSecret(Request $request)
    {
        // Validate JWT token
        $token = $request->bearerToken();
        if (!$token) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        try {
            $decoded = JWT::decode($token, env('APP_SECRET'), ['HS256']);
            $userId = $decoded->sub; // Get user ID from token
        } catch (ExpiredException $e) {
            return response()->json(['message' => 'Token has expired'], 401);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $validator = Validator::make($request->all(), [
            'secret' => 'required',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid data'], 400);
        }

        $encryptedSecret = encrypt($request->secret);
        Secret::create([
            'user_id' => $userId,
            'secret' => $encryptedSecret,
        ]);

        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        // Validate JWT token
        $token = $request->bearerToken();
        if (!$token) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        try {
            $decoded = JWT::decode($token, env('APP_SECRET'), ['HS256']);
            $userId = $decoded->sub; // Get user ID from token
        } catch (ExpiredException $e) {
            return response()->json(['message' => 'Token has expired'], 401);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Invalid authentication token'], 401);
        }

        $secret = Secret::where('user_id', $userId)->first();

        return response()->json(['secret' => $secret ? decrypt($secret->secret) : 'No secret found'], 200);
    }
}