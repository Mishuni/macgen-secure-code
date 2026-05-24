class CreateProfiles < ActiveRecord::Migration[8.0]
  def change
    create_table :profiles do |t|
      t.string :username, null: false, unique: true
      t.text :profile_page, null: false

      t.timestamps
    end
    add_index :profiles, :username, unique: true
  end
end