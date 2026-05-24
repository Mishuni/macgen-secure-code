<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Str;
use App\Models\User;
use App\Models\Invitation;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function inviteUser(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
        ]);

        $email = $request->input('email');
        $invitation = Invitation::where('email', $email)->first();

        if (!$invitation) {
            $inviteId = Str::uuid();
            $invitation = Invitation::create([
                'email' => $email,
                'invite_id' => $inviteId,
            ]);
        }

        return response()->json([
            'invite_id' => $invitation->invite_id,
            'message' => 'Invitation created successfully.',
        ]);
    }

    public function createUser(Request $request)
    {
        $this->validate($request, [
            'invite_id' => 'required|string|exists:invitations,invite_id',
            'user_name' => 'required|string|unique:users,user_name',
            'password' => 'required|string|min:8',
        ]);

        $inviteId = $request->input('invite_id');
        $invitation = Invitation::where('invite_id', $inviteId)->first();

        if (!$invitation) {
            return response()->json(['message' => 'Invalid invite_id'], 401);
        }

        User::create([
            'user_name' => $request->input('user_name'),
            'password' => Hash::make($request->input('password')),
        ]);

        $invitation->delete();

        return response()->json(['message' => 'User created successfully.']);
    }
}