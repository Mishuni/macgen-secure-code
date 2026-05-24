class CreateEntries < ActiveRecord::Migration[7.0]
  def change
    create_table :entries do |t|
      t.string :title, null: false
      t.text :content, null: false
      t.string :lastModifiedBy, null: false
      t.datetime :lastModifiedAt, null: false, default: -> { 'CURRENT_TIMESTAMP' }

      t.timestamps
    end
  end
end