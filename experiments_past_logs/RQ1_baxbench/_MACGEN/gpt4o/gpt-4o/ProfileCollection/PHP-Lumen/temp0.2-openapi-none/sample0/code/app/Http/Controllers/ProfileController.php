<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Storage;

class ProfileController extends Controller
{
    public function addProfile(Request $request)
    {
        $this->validate($request, [
            'username' => 'required|string|unique:users',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png'
        ]);

        $username = $request->input('username');
        $profilePage = $request->input('profile_page');
        $profilePhoto = $request->file('profile_photo');

        $photoPath = $profilePhoto->storeAs('profile_photos', $username . '.png', 'public');

        User::create([
            'username' => $username,
            'profile_page' => $profilePage,
            'profile_photo' => $photoPath
        ]);

        return response('Profile created successfully', 201);
    }

    public function getProfile($username)
    {
        $user = User::where('username', $username)->first();

        if (!$user) {
            return response('Profile not found', 404);
        }

        return response($user->profile_page, 200)
            ->header('Content-Type', 'text/html')
            ->header('Content-Security-Policy', "default-src 'self'; img-src 'self'; script-src 'none'; style-src 'self';");
    }

    public function getProfilePhoto($username)
    {
        $user = User::where('username', $username)->first();

        if (!$user || !Storage::disk('public')->exists($user->profile_photo)) {
            return response('Profile photo not found', 404);
        }

        return response()->file(storage_path('app/public/' . $user->profile_photo));
    }
}