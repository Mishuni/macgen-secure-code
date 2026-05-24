class RatingsController < ApplicationController
  def create
    @recipe = Recipe.find(params[:recipe_id])
    rating_params = params.require(:rating).permit(:rating)
    @rating = @recipe.ratings.build(rating_params)

    if @rating.save
      render json: { message: 'Rating added successfully' }, status: :created
    else
      render json: { errors: @rating.errors.full_messages }, status: :bad_request
    end
  end
end