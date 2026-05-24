class CommentsController < ApplicationController
  def create
    @recipe = Recipe.find(params[:recipe_id])
    @comment = @recipe.comments.new(comment_params)
    if @comment.save
      render json: { message: 'Comment added successfully' }, status: :created
    else
      render json: { error: @comment.errors.full_messages }, status: :bad_request
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  private

  def comment_params
    params.require(:comment).permit(:comment)
  end
end