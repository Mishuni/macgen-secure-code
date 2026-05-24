class EntriesController < ApplicationController
  before_action :set_entry, only: [:show, :update, :edit_history]

  # GET /entries
  def index
    @entries = Entry.all
    render json: @entries.map { |entry| { title: entry.title, link: entry_url(entry) } }
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

  # GET /entries/:id
  def show
    render json: @entry
  end

  # PUT /entries/:id
  def update
    if @entry.update(update_entry_params)
      render json: @entry
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  # GET /entries/:id/edits
  def edit_history
    @edits = @entry.edits
    render json: @edits
  end

  private

  def set_entry
    @entry = Entry.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Entry not found' }, status: :not_found
  end

  def entry_params
    params.require(:entry).permit(:title, :content, :createdBy)
  end

  def update_entry_params
    params.require(:entry).permit(:content, :modifiedBy)
  end
end