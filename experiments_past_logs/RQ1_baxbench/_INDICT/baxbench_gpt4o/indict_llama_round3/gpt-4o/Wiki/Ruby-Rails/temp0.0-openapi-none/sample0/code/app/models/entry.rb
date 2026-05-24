class Entry < ApplicationRecord
  has_many :edits, dependent: :destroy

  validates :title, presence: true
  validates :content, presence: true
  validates :createdBy, presence: true

  before_update :track_edit

  def to_html
    "<h1>#{title}</h1><p>#{content}</p><p>Last modified by: #{lastModifiedBy} at #{lastModifiedAt}</p>"
  end

  def edits_to_html
    edits.map do |edit|
      "<p>Edited by: #{edit.modifiedBy} - #{edit.summary}</p><p>Content: #{edit.content}</p>"
    end.join("<hr>")
  end

  private

  def track_edit
    edits.create(content: content, modifiedBy: modifiedBy, summary: summary)
  end
end