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
            'username' => 'required|string|unique:users,username',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png|max:2048',
        ]);

        if ($validator->fails()) {
            return response()->json(['message' => 'Invalid input', 'errors' => $validator->errors()], 400);
        }

        $profilePhotoPath = $request->file('profile_photo')->store('profile_photos');

        User::create([
            'username' => htmlspecialchars($request->username),
            'profile_page' => htmlspecialchars($request->profile_page),
            'profile_photo' => $profilePhotoPath,
        ]);

        return response()->json(['message' => 'Profile created successfully'], 201);
    }

    public function getProfile($username)
    {
        $user = User::where('username', htmlspecialchars($username))->first();

        if (!$user) {
            return response()->json(['message' => 'Profile not found'], 404);
        }

        return response($user->profile_page, 200)->header('Content-Type', 'text/html');
    }

    public function getProfilePhoto($username)
    {
        $user = User::where('username', htmlspecialchars($username))->first();

        if (!$user || !Storage::exists($user->profile_photo)) {
            return response()->json(['message' => 'Profile photo not found'], 404);
        }

        return response()->file(storage_path('app/' . $user->profile_photo));
    }
}