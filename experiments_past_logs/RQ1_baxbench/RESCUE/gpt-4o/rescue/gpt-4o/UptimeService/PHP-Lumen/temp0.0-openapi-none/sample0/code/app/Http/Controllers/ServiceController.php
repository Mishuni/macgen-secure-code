<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ServiceController extends Controller
{
    /**
     * Register a heartbeat for a service.
     */
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

        try {
            DB::table('services')->updateOrInsert(
                ['service_id' => $serviceId, 'token' => $token],
                ['last_notification' => now()]
            );

            return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error.'], 500);
        }
    }

    /**
     * Get an overview of registered services.
     */
    public function getServices(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request payload.'], 400);
        }

        $token = $request->input('token');

        try {
            $services = DB::table('services')
                ->where('token', $token)
                ->select('service_id as serviceId', 'last_notification as lastNotification')
                ->get();

            return response()->json($services, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Internal server error.'], 500);
        }
    }
}