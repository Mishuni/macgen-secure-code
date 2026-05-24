<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Illuminate\Support\Facades\Auth;

class AuthServiceProvider extends ServiceProvider
{
    public function boot()
    {
        Auth::viaRequest('api', function ($request) {
            $token = $request->bearerToken();
            if (!$token) {
                return null;
            }

            try {
                $credentials = JWT::decode($token, new Key(env('APP_SECRET'), 'HS256'));
                return User::find($credentials->sub);
            } catch (\Exception $e) {
                return null;
            }
        });
    }
}