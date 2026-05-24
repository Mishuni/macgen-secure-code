class CreateUsers < ActiveRecord::Migration[8.0]
  def change
    create_table :users do |t|
      t.string :user_name, null: false, unique: true
      t.string :password, null: false

      t.timestamps
    end
  end
end