<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class ServiceController extends Controller
{
    public function registerHeartbeat(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'serviceId' => 'required|string|max:255',
            'token' => 'required|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request payload.'], 400);
        }

        $serviceId = $request->input('serviceId');
        $token = $request->input('token');

        DB::table('services')->updateOrInsert(
            ['serviceId' => $serviceId],
            ['lastNotification' => now(), 'token' => $token]
        );

        return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
    }

    public function getServices(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request payload.'], 400);
        }

        $token = $request->input('token');

        $services = DB::table('services')
            ->where('token', $token)
            ->get(['serviceId', 'lastNotification']);

        return response()->json($services, 200);
    }
}