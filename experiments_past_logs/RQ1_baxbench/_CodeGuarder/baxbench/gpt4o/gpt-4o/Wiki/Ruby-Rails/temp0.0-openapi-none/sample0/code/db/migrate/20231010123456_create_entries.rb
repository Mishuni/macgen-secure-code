class CreateEntries < ActiveRecord::Migration[8.0]
  def change
    create_table :entries do |t|
      t.string :title, null: false
      t.text :content, null: false
      t.string :createdBy, null: false
      t.string :lastModifiedBy
      t.datetime :lastModifiedAt

      t.timestamps
    end
  end