<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class RecipeController extends Controller
{
    public function index()
    {
        $recipes = DB::table('recipes')->select('id', 'title')->get();
        return response()->json($recipes);
    }

    public function upload(Request $request)
    {
        $request->validate([
            'title' => 'required|string',
            'ingredients' => 'required|array',
            'instructions' => 'required|string',
        ]);

        $recipeId = DB::table('recipes')->insertGetId([
            'title' => $request->title,
            'ingredients' => json_encode($request->ingredients),
            'instructions' => $request->instructions,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['id' => $recipeId], 201);
    }

    public function show($recipeId)
    {
        $recipe = DB::table('recipes')->where('id', $recipeId)->first();
        if (!$recipe) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        $recipe->ingredients = json_decode($recipe->ingredients);
        return response()->json($recipe);
    }

    public function addComment(Request $request, $recipeId)
    {
        $request->validate([
            'comment' => 'required|string',
        ]);

        $recipeExists = DB::table('recipes')->where('id', $recipeId)->exists();
        if (!$recipeExists) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        DB::table('comments')->insert([
            'recipe_id' => $recipeId,
            'comment' => $request->comment,
            'created_at' => now(),
        ]);

        return response()->json(['message' => 'Comment added successfully'], 201);
    }

    public function rateRecipe(Request $request, $recipeId)
    {
        $request->validate([
            'rating' => 'required|integer|min:1|max:5',
        ]);

        $recipeExists = DB::table('recipes')->where('id', $recipeId)->exists();
        if (!$recipeExists) {
            return response()->json(['message' => 'Recipe not found'], 404);
        }

        DB::table('ratings')->insert([
            'recipe_id' => $recipeId,
            'rating' => $request->rating,
            'created_at' => now(),
        ]);

        return response()->json(['message' => 'Rating added successfully'], 201);
    }
}