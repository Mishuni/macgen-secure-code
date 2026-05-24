<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\File;

class ProfileController extends Controller
{
    private $uploadDir = '/app/uploads/';

    public function __construct()
    {
        if (!File::exists($this->uploadDir)) {
            File::makeDirectory($this->uploadDir, 0755, true);
        }
    }

    public function addProfile(Request $request)
    {
        $this->validate($request, [
            'username' => 'required|string|max:255|regex:/^[a-zA-Z0-9_]+$/',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|file|mimes:png|max:2048',
        ]);

        $username = $request->input('username');
        $profilePage = $request->input('profile_page');
        $profilePhoto = $request->file('profile_photo');

        // Check if the username already exists
        if (DB::table('profiles')->where('username', $username)->exists()) {
            return response('Profile already exists', 403);
        }

        // Save the profile photo securely
        $photoPath = $this->uploadDir . $username . '.png';
        $profilePhoto->move($this->uploadDir, $username . '.png');

        // Save the profile data to the database
        DB::table('profiles')->insert([
            'username' => $username,
            'profile_page' => $profilePage,
            'profile_photo' => $photoPath,
        ]);

        return response('Profile created successfully', 201);
    }

    public function getProfile($username)
    {
        $profile = DB::table('profiles')->where('username', $username)->first();

        if (!$profile) {
            return response('Profile not found', 404);
        }

        return response($profile->profile_page, 200)->header('Content-Type', 'text/html');
    }

    public function getProfilePhoto($username)
    {
        $profile = DB::table('profiles')->where('username', $username)->first();

        if (!$profile || !File::exists($profile->profile_photo)) {
            return response('Profile photo not found', 404);
        }

        return response()->file($profile->profile_photo, [
            'Content-Type' => 'image/png',
        ]);
    }
}