class CreateMessages < ActiveRecord::Migration[8.0]
  def change
    create_table :messages do |t|
      t.string :content, null: false, limit: 500
      t.string :username, null: false, limit: 50
      t.timestamps
    end
  end
end