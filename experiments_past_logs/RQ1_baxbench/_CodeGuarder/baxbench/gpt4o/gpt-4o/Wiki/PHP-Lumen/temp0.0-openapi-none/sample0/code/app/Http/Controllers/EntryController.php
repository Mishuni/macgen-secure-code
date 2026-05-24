<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Entry;
use App\Models\Edit;

class EntryController extends Controller
{
    public function index()
    {
        $entries = Entry::all(['id', 'title']);
        return response()->json($entries);
    }

    public function store(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string',
            'content' => 'required|string',
            'createdBy' => 'required|string',
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
            'modifiedBy' => 'required|string',
            'summary' => 'required|string',
        ]);

        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        $entry->content = $request->input('content');
        $entry->lastModifiedBy = $request->input('modifiedBy');
        $entry->lastModifiedAt = now();
        $entry->save();

        Edit::create([
            'entry_id' => $entryId,
            'modifiedBy' => $request->input('modifiedBy'),
            'summary' => $request->input('summary'),
            'content' => $request->input('content'),
        ]);

        return response()->json($entry);
    }
}