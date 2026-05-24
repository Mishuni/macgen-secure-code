class CreateEdits < ActiveRecord::Migration[8.0]
  def change
    create_table :edits do |t|
      t.references :entry, null: false, foreign_key: true
      t.text :content, null: false
      t.string :modifiedBy, null: false
      t.string :summary, null: false

      t.timestamps
    end
  end
end