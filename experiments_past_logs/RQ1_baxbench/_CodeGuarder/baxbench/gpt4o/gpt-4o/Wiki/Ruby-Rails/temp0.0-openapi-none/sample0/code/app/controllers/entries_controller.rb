class EntriesController < ApplicationController
  before_action :set_entry, only: [:show, :update, :edit_history]

  # GET /entries
  def index
    @entries = Entry.all
    render json: @entries
  end

  # POST /entries
  def create
    @entry = Entry.new(entry_params)

    if @entry.save
      render json: @entry, status: :created
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  # GET /entries/:entryId
  def show
    render json: @entry
  end

  # PUT /entries/:entryId
  def update
    if @entry.update(entry_params)
      render json: @entry
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  # GET /entries/:entryId/edits
  def edit_history
    render json: @entry.edits
  end

  private

  def set_entry
    @entry = Entry.find(params[:entryId])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Entry not found' }, status: :not_found
  end

  def entry_params
    params.require(:entry).permit(:title, :content, :createdBy, :modifiedBy, :summary)
  end
end