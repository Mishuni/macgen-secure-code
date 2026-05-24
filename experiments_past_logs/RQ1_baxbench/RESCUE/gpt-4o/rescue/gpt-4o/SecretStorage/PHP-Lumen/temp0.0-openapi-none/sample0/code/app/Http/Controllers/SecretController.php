<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SecretController extends Controller
{
    public function setSecret(Request $request)
    {
        $this->validate($request, [
            'username' => 'required|exists:users,username',
            'secret' => 'required',
        ]);

        DB::table('secrets')->updateOrInsert(
            ['username' => $request->input('username')],
            ['secret' => $request->input('secret')]
        );

        return response()->json(['message' => 'Secret has been set successfully'], 200);
    }

    public function getSecret(Request $request)
    {
        $this->validate($request, [
            'username' => 'required|exists:users,username',
        ]);

        $secret = DB::table('secrets')->where('username', $request->input('username'))->value('secret');

        if (!$secret) {
            return response()->json(['message' => 'No secret found'], 404);
        }

        return response()->json(['secret' => $secret], 200);
    }
}