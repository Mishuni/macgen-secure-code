<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class HeartbeatController extends Controller
{
    public function registerHeartbeat(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'serviceId' => 'required|string',
            'token' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request payload.'], 400);
        }

        $serviceId = $request->input('serviceId');
        $token = $request->input('token');

        // Store the heartbeat in the database
        DB::table('services')->updateOrInsert(
            ['serviceId' => $serviceId],
            ['lastNotification' => now(), 'token' => $token]
        );

        return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
    }
}