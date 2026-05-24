<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;

class ProfileController extends Controller
{
    public function addProfile(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'username' => 'required|string|unique:profiles',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png|max:2048',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid input'], 400);
        }

        // Sanitize HTML input
        $profile_page = htmlspecialchars($request->profile_page, ENT_QUOTES, 'UTF-8');

        $profilePhotoPath = $request->file('profile_photo')->store('profile_photos');

        User::create([
            'username' => $request->username,
            'profile_page' => $profile_page,
            'profile_photo' => $profilePhotoPath,
        ]);

        return response()->json(['message' => 'Profile created successfully'], 201);
    }

    public function getProfile($username)
    {
        $profile = User::where('username', $username)->first();

        if (!$profile) {
            return response()->json(['message' => 'Profile not found'], 404);
        }

        return response($profile->profile_page, 200)->header('Content-Type', 'text/html');
    }

    public function getProfilePhoto($username)
    {
        $profile = User::where('username', $username)->first();

        if (!$profile || !Storage::exists($profile->profile_photo)) {
            return response()->json(['message' => 'Profile photo not found'], 404);
        }

        return response()->file(storage_path('app/' . $profile->profile_photo), ['Content-Type' => 'image/png']);
    }
}