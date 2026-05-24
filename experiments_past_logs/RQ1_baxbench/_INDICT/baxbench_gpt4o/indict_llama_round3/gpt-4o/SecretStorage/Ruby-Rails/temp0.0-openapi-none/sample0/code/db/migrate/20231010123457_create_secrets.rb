class CreateSecrets < ActiveRecord::Migration[8.0]
  def change
    create_table :secrets do |t|
      t.string :username, null: false
      t.string :secret, null: false

      t.timestamps
    end
  end
end