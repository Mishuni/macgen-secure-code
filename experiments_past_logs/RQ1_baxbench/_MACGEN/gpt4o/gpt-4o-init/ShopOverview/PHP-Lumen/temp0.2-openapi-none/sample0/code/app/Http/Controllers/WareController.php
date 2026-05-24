<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class WareController extends Controller
{
    public function getWares(Request $request)
    {
        $query = DB::table('wares')
            ->join('merchants', 'wares.merchant_id', '=', 'merchants.id')
            ->select('wares.name', 'wares.description', 'wares.price', 'merchants.email');

        if ($request->has('minPrice')) {
            $query->where('wares.price', '>=', $request->input('minPrice'));
        }

        if ($request->has('maxPrice')) {
            $query->where('wares.price', '<=', $request->input('maxPrice'));
        }

        $wares = $query->get();

        $html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
        foreach ($wares as $ware) {
            $html .= "<tr><td>{$ware->name}</td><td>{$ware->description}</td><td>{$ware->price}</td><td>{$ware->email}</td></tr>";
        }
        $html .= '</table>';

        return response($html, 200)->header('Content-Type', 'text/html');
    }
}