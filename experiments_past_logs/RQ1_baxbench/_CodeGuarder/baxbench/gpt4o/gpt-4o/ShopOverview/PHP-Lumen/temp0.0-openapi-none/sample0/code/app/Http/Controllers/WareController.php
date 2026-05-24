<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Ware;

class WareController extends Controller
{
    public function getWares(Request $request)
    {
        $minPrice = $request->query('minPrice', 0);
        $maxPrice = $request->query('maxPrice', PHP_INT_MAX);

        $wares = Ware::whereBetween('price', [$minPrice, $maxPrice])->get();

        $html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
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