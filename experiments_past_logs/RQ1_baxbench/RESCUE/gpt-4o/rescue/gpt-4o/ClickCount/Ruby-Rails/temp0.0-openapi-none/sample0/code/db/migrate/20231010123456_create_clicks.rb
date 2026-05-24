class CreateClicks < ActiveRecord::Migration[8.0]
  def change
    create_table :clicks do |t|
      t.datetime :timestamp, null: false

      t.timestamps
    end
  end
end