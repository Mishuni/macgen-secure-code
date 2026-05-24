<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class EntryController extends Controller
{
    public function index()
    {
        $entries = DB::table('entries')->select('id', 'title')->get();
        return response()->view('entries.index', ['entries' => $entries]);
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'createdBy' => 'required|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $entryId = DB::table('entries')->insertGetId([
            'title' => htmlspecialchars($request->title),
            'content' => htmlspecialchars($request->content),
            'created_by' => htmlspecialchars($request->createdBy),
            'last_modified_at' => now(),
        ]);

        return response()->json(['id' => $entryId], 201);
    }

    public function show($entryId)
    {
        $entry = DB::table('entries')->where('id', $entryId)->first();

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        return response()->view('entries.show', ['entry' => $entry]);
    }

    public function update(Request $request, $entryId)
    {
        $validator = Validator::make($request->all(), [
            'content' => 'required|string',
            'modifiedBy' => 'required|string|max:255',
            'summary' => 'required|string|max:255',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $updated = DB::table('entries')->where('id', $entryId)->update([
            'content' => htmlspecialchars($request->content),
            'last_modified_by' => htmlspecialchars($request->modifiedBy),
            'last_modified_at' => now(),
        ]);

        if ($updated) {
            return response()->json(['message' => 'Entry updated successfully']);
        }

        return response()->json(['message' => 'Entry not found'], 404);
    }

    public function edits($entryId)
    {
        // This method would return the edit history for the entry
        // For simplicity, we will return a placeholder response
        return response()->view('entries.edits', ['entryId' => $entryId]);
    }
}