class Recipes::RatingsController < ApplicationController
  before_action :set_recipe

  def create
    rating = @recipe.ratings.new(rating_params)
    if rating.save
      render json: rating, status: :created
    else
      render json: { errors: rating.errors.full_messages }, status: :unprocessable_entity
    end
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:recipe_id])
  end

  def rating_params
    params.require(:rating).permit(:rating)
  end
end