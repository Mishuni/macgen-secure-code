<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class MessageController extends Controller
{
    public function index(Request $request)
    {
        $limit = $request->query('limit', 10);
        $offset = $request->query('offset', 0);
        $sort = $request->query('sort', 'DESC');

        // Validate sort parameter
        if (!in_array($sort, ['ASC', 'DESC'])) {
            return response()->json(['error' => 'Invalid sort parameter'], 400);
        }

        $messages = DB::select("SELECT * FROM messages ORDER BY created_at $sort LIMIT ? OFFSET ?", [$limit, $offset]);

        return response()->json($messages);
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'content' => 'required|string',
            'username' => 'required|string',
        ]);

        DB::insert('INSERT INTO messages (content, username, created_at) VALUES (?, ?, ?)', [
            $data['content'],
            $data['username'],
            now(),
        ]);

        return response()->json(['message' => 'Message posted successfully'], 200);
    }
}