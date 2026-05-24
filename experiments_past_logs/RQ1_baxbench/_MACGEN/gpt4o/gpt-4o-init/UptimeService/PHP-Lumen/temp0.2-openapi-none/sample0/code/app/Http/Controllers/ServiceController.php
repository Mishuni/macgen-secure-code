<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Service;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ServiceController extends Controller
{
    public function registerHeartbeat(Request $request)
    {
        $this->validate($request, [
            'serviceId' => 'required|string',
            'token' => 'required|string|regex:/^[a-zA-Z0-9]+$/',
        ]);

        try {
            $service = Service::updateOrCreate(
                ['service_id' => $request->serviceId, 'token' => $request->token],
                ['last_notification' => Carbon::now()]
            );

            return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Internal server error.'], 500);
        }
    }

    public function getServices(Request $request)
    {
        $this->validate($request, [
            'token' => 'required|string|regex:/^[a-zA-Z0-9]+$/',
        ]);

        try {
            $services = Service::where('token', $request->token)->get(['service_id', 'last_notification']);

            return response()->json($services, 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Internal server error.'], 500);
        }
    }
}