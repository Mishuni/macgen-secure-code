<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Message;

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

        $htmlResponse = '<ul>';
        foreach ($messages as $message) {
            $htmlResponse .= '<li><strong>' . htmlspecialchars($message->username, ENT_QUOTES, 'UTF-8') . ':</strong> ' . htmlspecialchars($message->content, ENT_QUOTES, 'UTF-8') . '</li>';
        }
        $htmlResponse .= '</ul>';

        return response($htmlResponse, 200)->header('Content-Type', 'text/html');
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