class EntriesController < ApplicationController
  def index
    @entries = Entry.all
    render json: @entries
  end

  def create
    @entry = Entry.new(entry_params)
    if @entry.save
      render json: @entry, status: :created
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  def show
    @entry = Entry.find(params[:id])
    render json: @entry
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Entry not found' }, status: :not_found
  end

  def update
    @entry = Entry.find(params[:id])
    if @entry.update(entry_params)
      render json: @entry
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Entry not found' }, status: :not_found
  end

  private

  def entry_params
    params.require(:entry).permit(:title, :content, :lastModifiedBy)
  end
end