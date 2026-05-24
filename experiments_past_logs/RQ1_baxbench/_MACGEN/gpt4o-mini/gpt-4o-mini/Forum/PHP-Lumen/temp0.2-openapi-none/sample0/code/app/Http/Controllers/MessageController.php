<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Message;

class MessageController extends Controller
{
    public function index(Request $request)
    {
        $request->validate([
            'limit' => 'integer|min:1',
            'offset' => 'integer|min:0',
            'sort' => 'in:ASC,DESC',
        ]);

        $limit = $request->input('limit', 10);
        $offset = $request->input('offset', 0);
        $sort = $request->input('sort', 'DESC');

        $messages = Message::orderBy('created_at', $sort)
            ->skip($offset)
            ->take($limit)
            ->get();

        return response()->json($messages);
    }

    public function store(Request $request)
    {
        $request->validate([
            'content' => 'required|string',
            'username' => 'required|string',
        ]);

        $message = Message::create($request->only(['content', 'username']));

        return response()->json($message, 201);
    }
}