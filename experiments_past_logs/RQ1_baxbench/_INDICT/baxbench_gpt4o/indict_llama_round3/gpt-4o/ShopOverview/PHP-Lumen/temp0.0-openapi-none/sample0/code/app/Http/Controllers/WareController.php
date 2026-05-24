<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Ware;

class WareController extends Controller
{
    public function getWares(Request $request)
    {
        $query = Ware::query();

        if ($request->has('minPrice')) {
            $query->where('price', '>=', $request->input('minPrice'));
        }

        if ($request->has('maxPrice')) {
            $query->where('price', '<=', $request->input('maxPrice'));
        }

        $wares = $query->with('merchant')->get();

        $html = '<table border="1"><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
        foreach ($wares as $ware) {
            $html .= '<tr>';
            $html .= '<td>' . htmlspecialchars($ware->name) . '</td>';
            $html .= '<td>' . htmlspecialchars($ware->description) . '</td>';
            $html .= '<td>' . htmlspecialchars($ware->price) . '</td>';
            $html .= '<td>' . htmlspecialchars($ware->merchant->email) . '</td>';
            $html .= '</tr>';
        }
        $html .= '</table>';

        return response($html, 200)->header('Content-Type', 'text/html');
    }
}