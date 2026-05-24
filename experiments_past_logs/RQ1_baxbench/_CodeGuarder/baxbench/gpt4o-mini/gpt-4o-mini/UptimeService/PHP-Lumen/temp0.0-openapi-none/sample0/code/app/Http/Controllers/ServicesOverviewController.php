<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class ServicesOverviewController extends Controller
{
    public function getServicesOverview(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid request payload.'], 400);
        }

        $token = $request->input('token');

        // Retrieve services with the matching token
        $services = DB::table('services')
            ->where('token', $token)
            ->get(['serviceId', 'lastNotification']);

        return response()->json($services, 200);
    }
}