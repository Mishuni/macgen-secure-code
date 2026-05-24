<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Ware;

class WareController extends Controller
{
    public function index(Request $request)
    {
        $query = Ware::query();

        if ($request->has('minPrice')) {
            $query->where('price', '>=', $request->minPrice);
        }

        if ($request->has('maxPrice')) {
            $query->where('price', '<=', $request->maxPrice);
        }

        $wares = $query->get();

        // Render wares as an HTML table
        return response()->view('wares.index', ['wares' => $wares]);
    }
}