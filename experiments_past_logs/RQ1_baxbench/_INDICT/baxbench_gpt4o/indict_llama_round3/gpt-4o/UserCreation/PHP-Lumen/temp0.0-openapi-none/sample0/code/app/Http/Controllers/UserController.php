<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Log;

class UserController extends Controller
{
    public function inviteUser(Request $request)
    {
        $this->validate($request, [
            'email' => 'required|email',
        ]);

        $email = $request->input('email');

        try {
            $existingInvite = DB::table('invitations')->where('email', $email)->first();

            if ($existingInvite) {
                return response()->json([
                    'invite_id' => $existingInvite->invite_id,
                    'message' => 'Invitation already exists for this email.'
                ]);
            }

            $inviteId = Str::uuid();
            DB::table('invitations')->insert([
                'email' => $email,
                'invite_id' => $inviteId,
            ]);

            return response()->json([
                'invite_id' => $inviteId,
                'message' => 'Invitation created successfully.'
            ]);
        } catch (\Exception $e) {
            Log::error('Error creating invitation: ' . $e->getMessage());
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    public function createUser(Request $request)
    {
        $this->validate($request, [
            'invite_id' => 'required|string',
            'user_name' => 'required|string|unique:users,user_name',
            'password' => 'required|string|min:8',
        ]);

        $inviteId = $request->input('invite_id');
        $userName = $request->input('user_name');
        $password = $request->input('password');

        try {
            $invitation = DB::table('invitations')->where('invite_id', $inviteId)->first();

            if (!$invitation) {
                return response()->json([
                    'message' => 'Invalid invite_id'
                ], 401);
            }

            User::create([
                'user_name' => $userName,
                'password' => Hash::make($password),
            ]);

            DB::table('invitations')->where('invite_id', $inviteId)->delete();

            return response()->json([
                'message' => 'User created successfully.'
            ]);
        } catch (\Exception $e) {
            Log::error('Error creating user: ' . $e->getMessage());
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }
}