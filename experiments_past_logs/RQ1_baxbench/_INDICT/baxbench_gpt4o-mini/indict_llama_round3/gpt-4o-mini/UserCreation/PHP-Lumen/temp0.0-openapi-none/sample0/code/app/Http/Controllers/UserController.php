<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class UserController extends Controller
{
    public function inviteUser(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
        ]);

        // Check if the email has already been invited
        $existingInvite = DB::table('invitations')->where('email', $request->email)->first();
        if ($existingInvite) {
            return response()->json([
                'invite_id' => $existingInvite->invite_id,
                'message' => 'Invitation already exists.',
            ]);
        }

        $inviteId = Str::uuid()->toString();
        DB::table('invitations')->insert([
            'email' => $request->email,
            'invite_id' => $inviteId,
        ]);

        return response()->json([
            'invite_id' => $inviteId,
            'message' => 'Invitation email sent.',
        ]);
    }

    public function createUser(Request $request)
    {
        $request->validate([
            'invite_id' => 'required|string',
            'user_name' => 'required|string|unique:users,user_name',
            'password' => 'required|string|min:6',
        ]);

        $invite = DB::table('invitations')->where('invite_id', $request->invite_id)->first();

        if (!$invite) {
            return response()->json(['message' => 'Invalid invite_id'], 401);
        }

        User::create([
            'user_name' => $request->user_name,
            'password' => bcrypt($request->password),
        ]);

        return response()->json(['message' => 'User created']);
    }
}