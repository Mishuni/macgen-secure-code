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
        $data = $request->validate([
            'title' => 'required|string',
            'content' => 'required|string',
            'createdBy' => 'required|string',
        ]);

        $entry = Entry::create($data + ['lastModifiedBy' => $data['createdBy'], 'lastModifiedAt' => now()]);
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
        $entry = Entry::find($entryId);
        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        $data = $request->validate([
            'content' => 'required|string',
            'modifiedBy' => 'required|string',
            'summary' => 'required|string',
        ]);

        $entry->update($data + ['lastModifiedBy' => $data['modifiedBy'], 'lastModifiedAt' => now()]);
        return response()->json($entry);
    }

    public function edits($entryId)
    {
        // This method would return the edit history of the entry
        // For simplicity, we will return a placeholder response
        return response()->json(['message' => 'Edit history not implemented yet.']);
    }
}