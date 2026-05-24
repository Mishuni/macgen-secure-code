<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Recipe;
use App\Models\Comment;
use App\Models\Rating;

class RecipeController extends Controller
{
    public function getRecipes()
    {
        $recipes = Recipe::all(['id', 'title']);
        return response()->json($recipes);
    }

    public function uploadRecipe(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string|max:255',
            'ingredients' => 'required|array',
            'instructions' => 'required|string',
        ]);

        $recipe = Recipe::create($request->all());
        return response()->json($recipe, 201);
    }

    public function getRecipe($recipeId)
    {
        $recipe = Recipe::with('comments', 'ratings')->find($recipeId);

        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        return response()->json($recipe);
    }

    public function addComment(Request $request, $recipeId)
    {
        $this->validate($request, [
            'comment' => 'required|string|max:500',
        ]);

        $recipe = Recipe::find($recipeId);

        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        $comment = new Comment($request->all());
        $recipe->comments()->save($comment);

        return response()->json(['message' => 'Comment added successfully'], 201);
    }

    public function rateRecipe(Request $request, $recipeId)
    {
        $this->validate($request, [
            'rating' => 'required|integer|min:1|max:5',
        ]);

        $recipe = Recipe::find($recipeId);

        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        $rating = new Rating($request->all());
        $recipe->ratings()->save($rating);

        return response()->json(['message' => 'Rating added successfully'], 201);
    }
}