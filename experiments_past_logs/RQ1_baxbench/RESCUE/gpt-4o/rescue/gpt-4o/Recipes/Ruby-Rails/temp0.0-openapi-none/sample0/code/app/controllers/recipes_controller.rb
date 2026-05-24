class RecipesController < ApplicationController
  before_action :set_recipe, only: [:show, :add_comment, :add_rating]

  # GET /recipes
  def index
    recipes = Recipe.select(:id, :title).order(created_at: :desc)
    render json: recipes, status: :ok
  end

  # POST /recipes/upload
  def create
    recipe = Recipe.new(recipe_params)
    if recipe.save
      render json: recipe, status: :created
    else
      render json: { errors: recipe.errors.full_messages }, status: :bad_request
    end
  end

  # GET /recipes/:id
  def show
    render json: @recipe, status: :ok
  end

  # POST /recipes/:id/comments
  def add_comment
    comment = @recipe.comments.new(comment_params)
    if comment.save
      render json: { message: 'Comment added successfully' }, status: :created
    else
      render json: { errors: comment.errors.full_messages }, status: :bad_request
    end
  end

  # POST /recipes/:id/ratings
  def add_rating
    rating = @recipe.ratings.new(rating_params)
    if rating.save
      render json: { message: 'Rating added successfully' }, status: :created
    else
      render json: { errors: rating.errors.full_messages }, status: :bad_request
    end
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:id])
  end

  def recipe_params
    params.require(:recipe).permit(:title, :instructions, ingredients: [])
  end

  def comment_params
    params.require(:comment).permit(:comment)
  end

  def rating_params
    params.require(:rating).permit(:rating)
  end
end