<?php

namespace App\Http\Controllers;

use App\Models\Edit;

class EditController extends Controller
{
    public function index($entryId)
    {
        $edits = Edit::where('entry_id', $entryId)->get();

        if ($edits->isEmpty()) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        return response()->json($edits);
    }
}