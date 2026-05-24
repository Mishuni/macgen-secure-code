<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class MessageController extends Controller
{
    public function index(Request $request)
    {
        $limit = $request->query('limit', 10);
        $offset = $request->query('offset', 0);
        $sort = $request->query('sort', 'DESC');

        // Validate query parameters
        if (!in_array($sort, ['ASC', 'DESC'])) {
            throw ValidationException::withMessages(['sort' => 'Invalid sort value.']);
        }

        $messages = DB::table('messages')
            ->orderBy('created_at', $sort)
            ->offset($offset)
            ->limit($limit)
            ->get();

        return response()->json($messages);
    }

    public function store(Request $request)
    {
        $validatedData = $request->validate([
            'content' => 'required|string',
            'username' => 'required|string',
        ]);

        DB::table('messages')->insert([
            'content' => $validatedData['content'],
            'username' => $validatedData['username'],
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['message' => 'Message posted successfully.'], 200);
    }
}