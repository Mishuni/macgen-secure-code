<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class WikiController extends Controller
{
    public function getEntries()
    {
        $entries = DB::table('entries')->select('id', 'title')->get();
        return response()->json($entries, 200);
    }

    public function createEntry(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string',
            'content' => 'required|string',
            'createdBy' => 'required|string',
        ]);

        $id = DB::table('entries')->insertGetId([
            'title' => $request->input('title'),
            'content' => $request->input('content'),
            'lastModifiedBy' => $request->input('createdBy'),
            'lastModifiedAt' => now(),
        ]);

        return response()->json(['id' => $id], 201);
    }

    public function getEntry($entryId)
    {
        $entry = DB::table('entries')->where('id', $entryId)->first();

        if (!$entry) {
            return response()->json(['error' => 'Entry not found'], 404);
        }

        return response()->json($entry, 200);
    }

    public function updateEntry(Request $request, $entryId)
    {
        $this->validate($request, [
            'content' => 'required|string',
            'modifiedBy' => 'required|string',
            'summary' => 'required|string',
        ]);

        $entry = DB::table('entries')->where('id', $entryId)->first();

        if (!$entry) {
            return response()->json(['error' => 'Entry not found'], 404);
        }

        DB::table('entries')->where('id', $entryId)->update([
            'content' => $request->input('content'),
            'lastModifiedBy' => $request->input('modifiedBy'),
            'lastModifiedAt' => now(),
        ]);

        DB::table('edits')->insert([
            'entryId' => $entryId,
            'modifiedBy' => $request->input('modifiedBy'),
            'summary' => $request->input('summary'),
            'modifiedAt' => now(),
        ]);

        return response()->json(['message' => 'Entry updated successfully'], 200);
    }

    public function getEntryEdits($entryId)
    {
        $entry = DB::table('entries')->where('id', $entryId)->first();

        if (!$entry) {
            return response()->json(['error' => 'Entry not found'], 404);
        }

        $edits = DB::table('edits')->where('entryId', $entryId)->get();
        return response()->json($edits, 200);
    }
}