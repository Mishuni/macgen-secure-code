class CreateSecrets < ActiveRecord::Migration[8.0]
  def change
    create_table :secrets do |t|
      t.references :user, null: false, foreign_key: true
      t.string :secret, null: false

      t.timestamps
    end
  end