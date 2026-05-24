class RatingsController < ApplicationController
  def create
    recipe = Recipe.find(params[:recipe_id])
    rating = recipe.ratings.new(rating_params)
    if rating.save
      render json: rating, status: :created
    else
      render json: { errors: rating.errors.full_messages }, status: :unprocessable_entity
    end
  end

  private

  def rating_params
    params.require(:rating).permit(:rating)
  end
end