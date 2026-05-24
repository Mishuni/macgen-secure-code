<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Entry;
use Illuminate\Support\Facades\Validator;

class EntryController extends Controller
{
    public function index()
    {
        return response()->json(Entry::all());
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'title' => 'required|string',
            'content' => 'required|string',
            'createdBy' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $entry = Entry::create($request->all());
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
        $validator = Validator::make($request->all(), [
            'content' => 'required|string',
            'modifiedBy' => 'required|string',
            'summary' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $entry = Entry::find($entryId);
        if (!$entry) {
            return response()->json(['message' => 'Entry not found'], 404);
        }

        $entry->content = $request->content;
        $entry->lastModifiedBy = $request->modifiedBy;
        $entry->lastModifiedAt = now();
        $entry->save();

        return response()->json($entry);
    }

    public function edits($entryId)
    {
        // Placeholder for edit history logic
        return response()->json(['message' => 'Edit history not implemented yet.'], 200);
    }
}