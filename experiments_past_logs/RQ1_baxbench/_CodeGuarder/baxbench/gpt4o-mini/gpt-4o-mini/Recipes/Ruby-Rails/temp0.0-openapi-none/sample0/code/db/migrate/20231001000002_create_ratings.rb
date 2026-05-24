class CreateRatings < ActiveRecord::Migration[8.0]
  def change
    create_table :ratings do |t|
      t.references :recipe, null: false, foreign_key: true
      t.integer :value, null: false

      t.timestamps
    end
  end
end