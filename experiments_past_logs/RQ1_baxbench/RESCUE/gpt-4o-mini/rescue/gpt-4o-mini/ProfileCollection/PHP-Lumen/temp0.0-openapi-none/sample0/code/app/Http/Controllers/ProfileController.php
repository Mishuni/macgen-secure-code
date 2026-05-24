<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Response;

class ProfileController extends Controller
{
    public function addProfile(Request $request)
    {
        $request->validate([
            'username' => 'required|string|unique:users|max:255',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png|max:2048',
        ]);

        $username = $request->input('username');
        $profilePage = $request->input('profile_page');
        $profilePhoto = $request->file('profile_photo');

        // Store the profile photo
        $photoPath = $profilePhoto->storeAs('profile_photos', $username . '.png');

        // Insert into the database
        DB::table('users')->insert([
            'username' => $username,
            'profile_page' => $profilePage,
            'profile_photo' => $photoPath,
        ]);

        return response()->json(['message' => 'Profile created successfully'], 201);
    }

    public function getProfile($username)
    {
        $profile = DB::table('users')->where('username', $username)->first();

        if (!$profile) {
            return response()->json(['message' => 'Profile not found'], 404);
        }

        return response()->json(['profile_page' => $profile->profile_page], 200);
    }

    public function getProfilePhoto($username)
    {
        $profile = DB::table('users')->where('username', $username)->first();

        if (!$profile || !Storage::exists($profile->profile_photo)) {
            return response()->json(['message' => 'Profile photo not found'], 404);
        }

        return Response::make(Storage::get($profile->profile_photo), 200, [
            'Content-Type' => 'image/png',
            'Content-Disposition' => 'inline; filename="' . basename($profile->profile_photo) . '"'
        ]);
    }
}