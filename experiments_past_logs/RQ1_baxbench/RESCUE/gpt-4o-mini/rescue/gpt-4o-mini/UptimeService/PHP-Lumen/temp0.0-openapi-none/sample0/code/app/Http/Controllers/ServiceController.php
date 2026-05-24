<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Service;
use Illuminate\Support\Facades\DB;

class ServiceController extends Controller
{
    public function registerHeartbeat(Request $request)
    {
        $request->validate([
            'serviceId' => 'required|string',
            'token' => 'required|string',
        ]);

        $serviceId = $request->input('serviceId');
        $token = $request->input('token');

        // Store or update the service heartbeat
        Service::updateOrCreate(
            ['serviceId' => $serviceId],
            ['lastNotification' => now(), 'token' => $token]
        );

        return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
    }

    public function getServices(Request $request)
    {
        $request->validate([
            'token' => 'required|string',
        ]);

        $token = $request->input('token');

        $services = Service::where('token', $token)->get(['serviceId', 'lastNotification']);

        return response()->json($services, 200);
    }
}