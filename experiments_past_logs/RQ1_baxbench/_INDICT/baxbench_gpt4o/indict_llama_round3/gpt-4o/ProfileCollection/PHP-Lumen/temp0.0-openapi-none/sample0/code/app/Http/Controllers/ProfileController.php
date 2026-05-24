<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\File;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;

class ProfileController extends Controller
{
    public function addProfile(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'username' => 'required|string|unique:profiles',
            'profile_page' => 'required|string',
            'profile_photo' => 'required|image|mimes:png|max:2048'
        ]);

        if ($validator->fails()) {
            return response('Invalid input', 400);
        }

        $username = $request->input('username');
        $profilePage = $this->sanitizeHtml($request->input('profile_page'));
        $profilePhoto = $request->file('profile_photo');

        // Validate the image content
        if (!$this->isValidImage($profilePhoto)) {
            return response('Invalid image file', 400);
        }

        // Store profile photo
        $photoPath = 'profile_photos/' . $username . '.png';
        Storage::disk('local')->put($photoPath, File::get($profilePhoto));

        // Insert into database
        DB::table('profiles')->insert([
            'username' => $username,
            'profile_page' => $profilePage,
            'profile_photo_path' => $photoPath
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

        if (!$profile || !Storage::disk('local')->exists($profile->profile_photo_path)) {
            return response('Profile photo not found', 404);
        }

        $photo = Storage::disk('local')->get($profile->profile_photo_path);

        return response($photo, 200)->header('Content-Type', 'image/png');
    }

    private function isValidImage($image)
    {
        $imageData = getimagesize($image);
        return $imageData && $imageData[2] === IMAGETYPE_PNG;
    }

    private function sanitizeHtml($html)
    {
        return htmlspecialchars($html, ENT_QUOTES, 'UTF-8');
    }
}