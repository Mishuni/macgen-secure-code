<?php

namespace App\Http\Controllers;

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

        $inviteId = Str::uuid()->toString();
        Invitation::create([
            'email' => $request->email,
            'invite_id' => $inviteId,
        ]);

        return response()->json([
            'invite_id' => $inviteId,
            'message' => 'Invitation email sent.',
        ]);
    }
}