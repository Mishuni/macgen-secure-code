<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Message;

class MessageController extends Controller
{
    public function index(Request $request)
    {
        $limit = (int) $request->query('limit', 10);
        $offset = (int) $request->query('offset', 0);
        $sort = strtoupper($request->query('sort', 'DESC'));

        // Validate sort parameter
        if (!in_array($sort, ['ASC', 'DESC'])) {
            return response()->json(['error' => 'Invalid sort parameter'], 400);
        }

        $messages = Message::orderBy('created_at', $sort)->skip($offset)->take($limit)->get();

        return response()->json($messages);
    }

    public function store(Request $request)
    {
        $request->validate([
            'content' => 'required|string',
            'username' => 'required|string',
        ]);

        $message = Message::create($request->all());

        return response()->json($message, 201);
    }
}