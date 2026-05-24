class CreateClicks < ActiveRecord::Migration[8.0]
  def change
    create_table :clicks, id: false do |t|
      t.string :id, primary_key: true
      t.datetime :timestamp, null: false

      t.timestamps
    end
  end
end