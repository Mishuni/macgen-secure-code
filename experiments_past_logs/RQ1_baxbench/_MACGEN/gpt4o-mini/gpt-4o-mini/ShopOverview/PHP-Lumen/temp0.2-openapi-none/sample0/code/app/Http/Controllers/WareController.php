<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Ware;

class WareController extends Controller
{
    public function upload(Request $request)
    {
        $request->validate([
            'csv' => 'required|string',
        ]);

        $csvData = str_getcsv($request->csv, "\n");
        foreach ($csvData as $line) {
            $data = str_getcsv($line);
            if (count($data) !== 3) {
                return response()->json(['error' => 'Invalid CSV format'], 400);
            }

            list($name, $description, $price) = $data;

            Ware::create([
                'name' => $name,
                'description' => $description,
                'price' => (float)$price,
                'merchant_id' => auth()->id(), // Assuming the merchant is authenticated
            ]);
        }

        return response()->json(['message' => 'Wares uploaded successfully']);
    }

    public function index(Request $request)
    {
        $query = Ware::query();

        if ($request->has('minPrice')) {
            $query->where('price', '>=', $request->minPrice);
        }

        if ($request->has('maxPrice')) {
            $query->where('price', '<=', $request->maxPrice);
        }

        $wares = $query->with('merchant')->get();

        return response()->view('wares.index', ['wares' => $wares]);
    }
}