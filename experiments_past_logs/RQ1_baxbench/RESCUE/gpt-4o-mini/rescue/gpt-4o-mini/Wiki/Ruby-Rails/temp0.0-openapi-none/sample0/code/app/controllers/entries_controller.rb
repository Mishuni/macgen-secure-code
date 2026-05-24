class EntriesController < ApplicationController
  before_action :set_entry, only: [:show, :update, :edits]

  def index
    entries = Entry.all
    render_json(entries)
  end

  def create
    entry_params = params.require(:entry).permit(:title, :content, :createdBy)
    entry = Entry.new(entry_params)
    if entry.save
      render_json(entry, :created)
    else
      render_json(entry.errors, :unprocessable_entity)
    end
  end

  def show
    render_json(@entry)
  end

  def update
    entry_params = params.require(:entry).permit(:content, :modifiedBy, :summary)
    if @entry.update(entry_params)
      render_json(@entry)
    else
      render_json(@entry.errors, :unprocessable_entity)
    end
  end

  def edits
    # Logic to retrieve edit history would go here
    render_json({ message: "Edit history not implemented" })
  end

  private

  def set_entry
    @entry = Entry.find_by(id: params[:id])
    not_found unless @entry
  end
end