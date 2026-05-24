<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;

class UserProfileController extends Controller
{
    public function addProfile(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'username' => 'required|string|unique:users|max:255',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png|max:2048',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 400);
        }

        $profilePhotoPath = $request->file('profile_photo')->store('profile_photos');

        User::create([
            'username' => $request->username,
            'profile_page' => $request->profile_page,
            'profile_photo' => $profilePhotoPath,
        ]);

        return response()->json(['message' => 'Profile created successfully'], 201);
    }

    public function getProfile($username)
    {
        $user = User::where('username', $username)->first();

        if (!$user) {
            return response()->json(['error' => 'Profile not found'], 404);
        }

        return response()->json(['profile_page' => $user->profile_page], 200);
    }

    public function getProfilePhoto($username)
    {
        $user = User::where('username', $username)->first();

        if (!$user || !Storage::exists($user->profile_photo)) {
            return response()->json(['error' => 'Profile photo not found'], 404);
        }

        return response()->download(storage_path('app/' . $user->profile_photo));
    }
}