class CreateProducts < ActiveRecord::Migration[8.0]
  def change
    create_table :products do |t|
      t.string :name, null: false
      t.jsonb :data, default: {}

      t.timestamps
    end
  end
end