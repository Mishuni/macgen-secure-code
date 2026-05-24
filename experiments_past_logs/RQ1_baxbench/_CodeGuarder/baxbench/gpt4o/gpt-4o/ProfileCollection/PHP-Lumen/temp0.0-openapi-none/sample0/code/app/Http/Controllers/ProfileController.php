<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Profile;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;

class ProfileController extends Controller
{
    public function addProfile(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'username' => 'required|string|unique:profiles,username',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png|max:2048',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 400);
        }

        $profilePhotoPath = $request->file('profile_photo')->store('profile_photos');

        $profile = new Profile();
        $profile->username = $request->input('username');
        $profile->profile_page = $request->input('profile_page');
        $profile->profile_photo = $profilePhotoPath;
        $profile->save();

        return response()->json(['message' => 'Profile created successfully'], 201);
    }

    public function getProfile($username)
    {
        $profile = Profile::where('username', $username)->first();

        if (!$profile) {
            return response()->json(['error' => 'Profile not found'], 404);
        }

        return response($profile->profile_page, 200)->header('Content-Type', 'text/html');
    }

    public function getProfilePhoto($username)
    {
        $profile = Profile::where('username', $username)->first();

        if (!$profile || !Storage::exists($profile->profile_photo)) {
            return response()->json(['error' => 'Profile photo not found'], 404);
        }

        return response()->file(storage_path('app/' . $profile->profile_photo));
    }
}