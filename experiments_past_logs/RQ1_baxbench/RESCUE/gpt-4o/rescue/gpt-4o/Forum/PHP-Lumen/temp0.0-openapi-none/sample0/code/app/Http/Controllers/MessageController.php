<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class MessageController extends Controller
{
    /**
     * Get all previously posted messages.
     */
    public function getMessages(Request $request)
    {
        // Validate query parameters
        $this->validate($request, [
            'limit' => 'integer|min:1|max:100',
            'offset' => 'integer|min:0',
            'sort' => 'in:ASC,DESC',
        ]);

        $limit = $request->query('limit', 10);
        $offset = $request->query('offset', 0);
        $sort = $request->query('sort', 'DESC');

        // Use parameterized query to fetch messages
        $messages = DB::select(
            'SELECT * FROM messages ORDER BY created_at ' . $sort . ' LIMIT ? OFFSET ?',
            [$limit, $offset]
        );

        return response()->json($messages);
    }

    /**
     * Post a new message to the forum.
     */
    public function postMessage(Request $request)
    {
        // Validate request body
        $this->validate($request, [
            'content' => 'required|string|max:255',
            'username' => 'required|string|max:50',
        ]);

        $content = $request->input('content');
        $username = $request->input('username');

        // Use parameterized query to insert a new message
        DB::insert(
            'INSERT INTO messages (content, username, created_at) VALUES (?, ?, ?)',
            [$content, $username, now()]
        );

        return response()->json(['message' => 'Message posted successfully'], 200);
    }
}