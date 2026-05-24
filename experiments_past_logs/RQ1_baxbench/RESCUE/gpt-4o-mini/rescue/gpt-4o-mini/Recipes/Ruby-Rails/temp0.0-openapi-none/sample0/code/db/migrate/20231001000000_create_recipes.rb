class CreateRecipes < ActiveRecord::Migration[7.0]
  def change
    create_table :recipes do |t|
      t.string :title
      t.text :instructions
      t.text :ingredients, array: true, default: []
      t.timestamps
    end
  end
end