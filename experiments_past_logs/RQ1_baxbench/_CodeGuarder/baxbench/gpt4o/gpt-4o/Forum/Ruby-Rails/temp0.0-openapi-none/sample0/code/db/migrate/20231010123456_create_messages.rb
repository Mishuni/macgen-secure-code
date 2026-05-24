class CreateMessages < ActiveRecord::Migration[8.0]
  def change
    create_table :messages do |t|
      t.string :content, null: false
      t.string :username, null: false

      t.timestamps
    end
  end
end