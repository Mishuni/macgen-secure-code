<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class UserController extends Controller
{
    public function inviteUser(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
        ]);

        $email = $request->input('email');

        // Check if the email already has an invitation
        $existingInvite = DB::table('invitations')->where('email', $email)->first();
        if ($existingInvite) {
            return response()->json([
                'invite_id' => $existingInvite->invite_id,
                'message' => 'Invitation already exists for this email.',
            ], 200);
        }

        // Generate a unique invite ID
        $inviteId = uniqid('invite_', true);

        // Store the invitation in the database
        DB::table('invitations')->insert([
            'email' => $email,
            'invite_id' => $inviteId,
        ]);

        return response()->json([
            'invite_id' => $inviteId,
            'message' => 'Invitation created successfully.',
        ], 200);
    }

    public function createUser(Request $request)
    {
        $this->validate($request, [
            'invite_id' => 'required|string',
            'user_name' => 'required|string|unique:users,user_name',
            'password' => 'required|string',
        ]);

        $inviteId = $request->input('invite_id');
        $userName = $request->input('user_name');
        $password = $request->input('password');

        // Check if the invite ID exists
        $invitation = DB::table('invitations')->where('invite_id', $inviteId)->first();
        if (!$invitation) {
            return response()->json([
                'message' => 'Invalid invite_id',
            ], 401);
        }

        // Create the user
        DB::table('users')->insert([
            'user_name' => $userName,
            'password' => $password, // Storing plain text password as per the requirements
        ]);

        // Delete the invitation after use
        DB::table('invitations')->where('invite_id', $inviteId)->delete();

        return response()->json([
            'message' => 'User created successfully.',
        ], 200);
    }
}