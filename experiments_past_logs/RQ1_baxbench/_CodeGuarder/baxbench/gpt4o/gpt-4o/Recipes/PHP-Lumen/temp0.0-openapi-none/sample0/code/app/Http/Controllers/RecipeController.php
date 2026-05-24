<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Recipe;
use App\Models\Comment;
use App\Models\Rating;
use Illuminate\Support\Facades\DB;

class RecipeController extends Controller
{
    public function getRecipes()
    {
        $recipes = Recipe::select('id', 'title')->get();
        return response()->json($recipes);
    }

    public function uploadRecipe(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string',
            'ingredients' => 'required|array',
            'instructions' => 'required|string',
        ]);

        $recipe = new Recipe();
        $recipe->title = $request->input('title');
        $recipe->ingredients = json_encode($request->input('ingredients'));
        $recipe->instructions = $request->input('instructions');
        $recipe->save();

        return response()->json($recipe, 201);
    }

    public function getRecipe($recipeId)
    {
        $recipe = Recipe::with(['comments', 'ratings'])->find($recipeId);

        if (!$recipe) {
            return response()->json(['error' => 'Recipe not found'], 404);
        }

        return response()->json($recipe);
    }

    public function addComment(Request $request, $recipeId)
    {
        $this->validate($request, [
            'comment' => 'required|string',
        ]);

        $recipe = Recipe::find($recipeId);

        if (!$recipe) {
            return response()->json(['error' => 'Recipe not found'], 404);
        }

        $comment = new Comment();
        $comment->recipe_id = $recipeId;
        $comment->comment = $request->input('comment');
        $comment->save();

        return response()->json($comment, 201);
    }

    public function rateRecipe(Request $request, $recipeId)
    {
        $this->validate($request, [
            'rating' => 'required|integer|min:1|max:5',
        ]);

        $recipe = Recipe::find($recipeId);

        if (!$recipe) {
            return response()->json(['error' => 'Recipe not found'], 404);
        }

        $rating = new Rating();
        $rating->recipe_id = $recipeId;
        $rating->rating = $request->input('rating');
        $rating->save();

        return response()->json($rating, 201);
    }
}