class PropertySerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode, 
  :total_units, :bbl, :bin, :rent_stabilized, :owner_id

end