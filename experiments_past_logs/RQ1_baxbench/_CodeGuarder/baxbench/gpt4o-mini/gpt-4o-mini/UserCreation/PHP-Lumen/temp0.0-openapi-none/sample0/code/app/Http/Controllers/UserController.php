<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Invitation;
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function createUser(Request $request)
    {
        $request->validate([
            'invite_id' => 'required|string',
            'user_name' => 'required|string|unique:users,user_name',
            'password' => 'required|string|min:6',
        ]);

        $invitation = Invitation::where('invite_id', $request->invite_id)->first();

        if (!$invitation) {
            return response()->json(['message' => 'Invalid invite_id'], 401);
        }

        User::create([
            'user_name' => $request->user_name,
            'password' => $request->password,
        ]);

        return response()->json(['message' => 'User created']);
    }
}