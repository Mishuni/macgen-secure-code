class CommentsController < ApplicationController
  before_action :set_recipe

  def create
    @comment = @recipe.comments.new(comment_params)
    if @comment.save
      render json: { message: 'Comment added successfully' }, status: :created
    else
      render json: { errors: @comment.errors.full_messages }, status: :bad_request
    end
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:recipe_id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  def comment_params
    params.require(:comment).permit(:comment)
  end
end