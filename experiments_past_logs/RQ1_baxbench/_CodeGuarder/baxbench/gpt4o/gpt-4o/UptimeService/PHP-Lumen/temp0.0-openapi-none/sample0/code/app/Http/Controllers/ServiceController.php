<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ServiceController extends Controller
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

        try {
            DB::table('services')->updateOrInsert(
                ['serviceId' => $request->input('serviceId')],
                ['token' => $request->input('token'), 'lastNotification' => now()]
            );

            return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error.'], 500);
        }
    }

    public function getServices(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request payload.'], 400);
        }

        try {
            $services = DB::table('services')
                ->where('token', $request->input('token'))
                ->get(['serviceId', 'lastNotification']);

            return response()->json($services, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error.'], 500);
        }
    }
}