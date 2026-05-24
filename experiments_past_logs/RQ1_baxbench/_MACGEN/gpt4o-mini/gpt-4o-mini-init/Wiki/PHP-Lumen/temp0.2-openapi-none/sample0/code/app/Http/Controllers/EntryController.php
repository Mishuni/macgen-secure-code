<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Entry;

class EntryController extends Controller
{
    public function index()
    {
        return response()->json(Entry::all());
    }

    public function store(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'createdBy' => 'required|string|max:255',
        ]);

        $entry = Entry::create($request->only(['title', 'content', 'createdBy']));

        return response()->json($entry, 201);
    }

    public function show($entryId)
    {
        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        return response()->json($entry);
    }

    public function update(Request $request, $entryId)
    {
        $this->validate($request, [
            'content' => 'required|string',
            'modifiedBy' => 'required|string|max:255',
            'summary' => 'required|string',
        ]);

        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        $entry->update($request->only(['content', 'modifiedBy']));

        return response()->json($entry);
    }

    public function edits($entryId)
    {
        // This method should return the edit history for the entry
        return response()->json(['message' => 'Edit history not implemented yet.']);
    }
}