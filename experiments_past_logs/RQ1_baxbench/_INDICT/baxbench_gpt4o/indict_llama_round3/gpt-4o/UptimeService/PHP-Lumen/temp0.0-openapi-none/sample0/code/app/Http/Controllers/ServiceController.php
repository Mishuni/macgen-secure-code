<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ServiceController extends Controller
{
    public function registerHeartbeat(Request $request)
    {
        $this->validate($request, [
            'serviceId' => 'required|string',
            'token' => 'required|string',
        ]);

        try {
            $hashedToken = hash('sha256', $request->input('token'));

            DB::table('services')->updateOrInsert(
                ['serviceId' => $request->input('serviceId')],
                ['token' => $hashedToken, 'lastNotification' => Carbon::now()]
            );

            return response()->json(['message' => 'Heartbeat registered successfully.'], 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Internal server error.'], 500);
        }
    }

    public function getServices(Request $request)
    {
        $this->validate($request, [
            'token' => 'required|string',
        ]);

        try {
            $hashedToken = hash('sha256', $request->input('token'));
            $services = DB::table('services')->where('token', $hashedToken)->get(['serviceId', 'lastNotification']);

            return response()->json($services, 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Internal server error.'], 500);
        }
    }
}