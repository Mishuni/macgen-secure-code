<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Entry;
use App\Models\Edit;
use Illuminate\Support\Facades\DB;

class WikiController extends Controller
{
    public function getAllEntries()
    {
        $entries = Entry::all(['id', 'title']);
        return response()->json($entries);
    }

    public function createEntry(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string',
            'content' => 'required|string',
            'createdBy' => 'required|string',
        ]);

        $entry = Entry::create([
            'title' => $request->title,
            'content' => $request->content,
            'lastModifiedBy' => $request->createdBy,
            'lastModifiedAt' => now(),
        ]);

        return response()->json($entry, 201);
    }

    public function getEntry($entryId)
    {
        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        return response()->json($entry);
    }

    public function updateEntry(Request $request, $entryId)
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

        DB::transaction(function () use ($entry, $request) {
            $entry->update([
                'content' => $request->content,
                'lastModifiedBy' => $request->modifiedBy,
                'lastModifiedAt' => now(),
            ]);

            Edit::create([
                'entry_id' => $entry->id,
                'content' => $request->content,
                'modifiedBy' => $request->modifiedBy,
                'summary' => $request->summary,
            ]);
        });

        return response()->json($entry);
    }

    public function getEntryEdits($entryId)
    {
        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        $edits = Edit::where('entry_id', $entryId)->get();
        return response()->json($edits);
    }
}