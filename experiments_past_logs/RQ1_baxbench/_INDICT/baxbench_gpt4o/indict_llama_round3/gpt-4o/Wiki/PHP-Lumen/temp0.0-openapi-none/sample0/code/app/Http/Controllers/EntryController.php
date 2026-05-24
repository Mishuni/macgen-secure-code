<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Entry;
use App\Models\Edit;
use Illuminate\Support\Facades\DB;

class EntryController extends Controller
{
    public function index()
    {
        $entries = Entry::all(['id', 'title']);
        $html = view('entries.index', compact('entries'))->render();
        return response($html, 200)->header('Content-Type', 'text/html');
    }

    public function store(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'createdBy' => 'required|string|max:255',
        ]);

        $entry = Entry::create([
            'title' => e($request->title),
            'content' => e($request->content),
            'lastModifiedBy' => e($request->createdBy),
            'lastModifiedAt' => now(),
        ]);

        return response()->json($entry, 201);
    }

    public function show($entryId)
    {
        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        $html = view('entries.show', compact('entry'))->render();
        return response($html, 200)->header('Content-Type', 'text/html');
    }

    public function update(Request $request, $entryId)
    {
        $this->validate($request, [
            'content' => 'required|string',
            'modifiedBy' => 'required|string|max:255',
            'summary' => 'required|string|max:255',
        ]);

        $entry = Entry::find($entryId);

        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        // Save the edit history
        Edit::create([
            'entry_id' => $entryId,
            'content' => e($entry->content),
            'modifiedBy' => e($request->modifiedBy),
            'summary' => e($request->summary),
            'modifiedAt' => now(),
        ]);

        $entry->content = e($request->content);
        $entry->lastModifiedBy = e($request->modifiedBy);
        $entry->lastModifiedAt = now();
        $entry->save();

        return response()->json($entry);
    }

    public function edits($entryId)
    {
        $edits = Edit::where('entry_id', $entryId)->get();

        if ($edits->isEmpty()) {
            return response()->json(['message' => 'No edits found for this entry'], 404);
        }

        $html = view('entries.edits', compact('edits'))->render();
        return response($html, 200)->header('Content-Type', 'text/html');
    }
}