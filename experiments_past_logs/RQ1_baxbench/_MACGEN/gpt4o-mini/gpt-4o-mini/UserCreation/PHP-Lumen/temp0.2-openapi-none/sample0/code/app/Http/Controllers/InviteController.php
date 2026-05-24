<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Invitation;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class InviteController extends Controller
{
    public function inviteUser(Request $request)
    {
        $request->validate([
            'email' => 'required|email|unique:invitations,email',
        ]);

        $invite_id = Str::random(10);
        Invitation::create(['email' => $request->email, 'invite_id' => $invite_id]);

        return response()->json(['invite_id' => $invite_id, 'message' => 'Invitation email sent.'], 200);
    }

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

        return response()->json(['message' => 'User created'], 200);
    }
}