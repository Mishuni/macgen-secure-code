<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Recipe;
use App\Models\Comment;
use App\Models\Rating;

class RecipeController extends Controller
{
    public function index()
    {
        $recipes = Recipe::all();
        return response()->json($recipes);
    }

    public function upload(Request $request)
    {
        $request->validate([
            'title' => 'required|string',
            'ingredients' => 'required|array',
            'instructions' => 'required|string',
        ]);

        $recipe = Recipe::create($request->all());
        return response()->json($recipe, 201);
    }

    public function show($recipeId)
    {
        $recipe = Recipe::with(['comments', 'ratings'])->find($recipeId);
        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }
        return response()->json($recipe);
    }

    public function addComment(Request $request, $recipeId)
    {
        $request->validate([
            'comment' => 'required|string',
        ]);

        $recipe = Recipe::find($recipeId);
        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        $comment = new Comment(['comment' => $request->comment]);
        $recipe->comments()->save($comment);
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

        $rating = new Rating(['rating' => $request->rating]);
        $recipe->ratings()->save($rating);
        return response()->json(['message' => 'Rating added successfully'], 201);
    }
}