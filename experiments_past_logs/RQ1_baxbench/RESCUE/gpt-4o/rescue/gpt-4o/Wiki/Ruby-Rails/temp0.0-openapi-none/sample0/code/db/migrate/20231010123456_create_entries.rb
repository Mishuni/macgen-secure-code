class CreateEntries < ActiveRecord::Migration[8.0]
  def change
    create_table :entries do |t|
      t.string :title, null: false
      t.text :content, null: false
      t.string :created_by, null: false
      t.string :modified_by
      t.datetime :last_modified_at

      t.timestamps
    end
  end
end