<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use App\Models\User;
use Illuminate\Support\Str;

class UserController extends Controller
{
    public function inviteUser(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email|unique:users,email',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid email or email already invited.'], 400);
        }

        $inviteId = Str::uuid()->toString();

        DB::table('invitations')->insert([
            'email' => $request->input('email'),
            'invite_id' => $inviteId,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['invite_id' => $inviteId, 'message' => 'Invitation created successfully.'], 200);
    }

    public function createUser(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'invite_id' => 'required|exists:invitations,invite_id',
            'user_name' => 'required|unique:users,user_name',
            'password' => 'required|min:8',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid invite_id or username already exists.'], 400);
        }

        $user = new User();
        $user->user_name = $request->input('user_name');
        $user->password = app('hash')->make($request->input('password'));
        $user->save();

        DB::table('invitations')->where('invite_id', $request->input('invite_id'))->delete();

        return response()->json(['message' => 'User created successfully.'], 200);
    }
}