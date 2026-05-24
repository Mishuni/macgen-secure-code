<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Recipe;
use Illuminate\Support\Facades\DB;

class RecipeController extends Controller
{
    public function index()
    {
        $recipes = Recipe::all();
        return response()->view('recipes.index', ['recipes' => $recipes]);
    }

    public function upload(Request $request)
    {
        $request->validate([
            'title' => 'required|string|max:255',
            'ingredients' => 'required|array',
            'instructions' => 'required|string',
        ]);

        $recipe = Recipe::create($request->all());
        return response()->json($recipe, 201);
    }

    public function show($recipeId)
    {
        $recipe = Recipe::find($recipeId);
        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }
        return response()->view('recipes.show', ['recipe' => $recipe]);
    }

    public function addComment(Request $request, $recipeId)
    {
        $request->validate([
            'comment' => 'required|string|max:255',
        ]);

        $recipe = Recipe::find($recipeId);
        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        $recipe->comments()->create(['comment' => $request->comment]);
        return response()->json(['message' => 'Comment added successfully'], 201);
    }

    public function rateRecipe(Request $request, $recipeId)
    {
        $request->validate([
            'rating' => 'required|integer|min:1|max:5',
        ]);

        $recipe = Recipe::find($recipeId);
        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        $recipe->ratings()->create(['rating' => $request->rating]);
        return response()->json(['message' => 'Rating added successfully'], 201);
    }
}