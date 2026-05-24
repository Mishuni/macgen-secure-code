<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Message;
use Illuminate\Support\Facades\Validator;

class MessageController extends Controller
{
    public function getMessages(Request $request)
    {
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
        $validator = Validator::make($request->all(), [
            'content' => 'required|string',
            'username' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => 'Invalid input'], 400);
        }

        $message = new Message();
        $message->content = $request->input('content');
        $message->username = $request->input('username');
        $message->save();

        return response()->json(['message' => 'Message posted successfully'], 200);
    }
}