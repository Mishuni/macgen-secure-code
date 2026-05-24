class CreateProfiles < ActiveRecord::Migration[7.0]
  def change
    create_table :profiles do |t|
      t.string :username, null: false
      t.text :profile_page, null: false

      t.timestamps
    end

    add_index :profiles, :username, unique: true
  end
end