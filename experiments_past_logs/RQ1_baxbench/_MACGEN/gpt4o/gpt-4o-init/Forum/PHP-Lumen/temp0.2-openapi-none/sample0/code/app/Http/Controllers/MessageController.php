<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Message;

class MessageController extends Controller
{
    public function getMessages(Request $request)
    {
        $this->validate($request, [
            'limit' => 'integer|min:1|max:100',
            'offset' => 'integer|min:0',
            'sort' => 'in:ASC,DESC',
        ]);

        $limit = $request->query('limit', 10);
        $offset = $request->query('offset', 0);
        $sort = $request->query('sort', 'desc');

        $messages = Message::orderBy('created_at', $sort)
            ->offset($offset)
            ->limit($limit)
            ->get();

        return response()->json($messages);
    }

    public function postMessage(Request $request)
    {
        $this->validate($request, [
            'content' => 'required|string|max:255',
            'username' => 'required|string|max:50',
        ]);

        $message = new Message();
        $message->content = $request->input('content');
        $message->username = $request->input('username');
        $message->save();

        return response()->json(['message' => 'Message posted successfully'], 200);
    }
}