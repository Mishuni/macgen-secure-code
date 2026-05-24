class CreateCreditCardPhoneAssociations < ActiveRecord::Migration[8.0]
  def change
    create_table :credit_card_phone_associations do |t|
      t.string :credit_card, null: false
      t.string :phone, null: false

      t.timestamps
    end

    add_index :credit_card_phone_associations, [:credit_card, :phone], unique: true
  end
end