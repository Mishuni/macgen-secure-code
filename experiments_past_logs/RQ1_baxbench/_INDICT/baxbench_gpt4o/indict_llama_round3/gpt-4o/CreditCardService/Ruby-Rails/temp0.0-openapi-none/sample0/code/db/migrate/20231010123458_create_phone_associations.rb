class CreatePhoneAssociations < ActiveRecord::Migration[8.0]
  def change
    create_table :phone_associations do |t|
      t.references :credit_card, null: false, foreign_key: true
      t.references :phone, null: false, foreign_key: true

      t.timestamps
    end
  end
end