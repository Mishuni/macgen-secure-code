class CreateClicks < ActiveRecord::Migration[7.0]
  def change
    create_table :clicks do |t|
      t.datetime :timestamp, null: false

      t.timestamps
    end
  end
end