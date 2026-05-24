<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class RecipeController extends Controller
{
    public function getRecipes()
    {
        try {
            $recipes = DB::table('recipes')
                ->select('id', 'title')
                ->get();

            return response()->json($recipes, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Server error'], 500);
        }
    }

    public function uploadRecipe(Request $request)
    {
        $this->validate($request, [
            'title' => 'required|string',
            'ingredients' => 'required|array',
            'instructions' => 'required|string',
        ]);

        try {
            $id = DB::table('recipes')->insertGetId([
                'title' => $request->input('title'),
                'ingredients' => json_encode($request->input('ingredients')),
                'instructions' => $request->input('instructions'),
            ]);

            return response()->json(['id' => $id], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    public function getRecipe($recipeId)
    {
        try {
            $recipe = DB::table('recipes')->where('id', $recipeId)->first();

            if (!$recipe) {
                return response()->json(['error' => 'Recipe not found'], 404);
            }

            $recipe->ingredients = json_decode($recipe->ingredients);
            $recipe->comments = DB::table('comments')->where('recipe_id', $recipeId)->get();
            $recipe->avgRating = DB::table('ratings')
                ->where('recipe_id', $recipeId)
                ->avg('rating');

            return response()->json($recipe, 200);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Server error'], 500);
        }
    }

    public function addComment(Request $request, $recipeId)
    {
        $this->validate($request, [
            'comment' => 'required|string',
        ]);

        try {
            $recipe = DB::table('recipes')->where('id', $recipeId)->first();

            if (!$recipe) {
                return response()->json(['error' => 'Recipe not found'], 404);
            }

            DB::table('comments')->insert([
                'recipe_id' => $recipeId,
                'comment' => $request->input('comment'),
            ]);

            return response()->json(['message' => 'Comment added successfully'], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }

    public function addRating(Request $request, $recipeId)
    {
        $this->validate($request, [
            'rating' => 'required|integer|min:1|max:5',
        ]);

        try {
            $recipe = DB::table('recipes')->where('id', $recipeId)->first();

            if (!$recipe) {
                return response()->json(['error' => 'Recipe not found'], 404);
            }

            DB::table('ratings')->insert([
                'recipe_id' => $recipeId,
                'rating' => $request->input('rating'),
            ]);

            return response()->json(['message' => 'Rating added successfully'], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid input'], 400);
        }
    }
}