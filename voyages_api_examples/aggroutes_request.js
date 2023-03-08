var myHeaders = new Headers();
myHeaders.append("Authorization", "Token XXXXXXXXXXXXX");

var formdata = new FormData();
formdata.append("cachename", "voyage_maps");
formdata.append("dataset", "0");
formdata.append("dataset", "0");
formdata.append("value_field_tuple", "voyage_slaves_numbers__imp_total_num_slaves_disembarked");
formdata.append("value_field_tuple", "sum");
formdata.append("groupby_fields", "voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id");
formdata.append("groupby_fields", "voyage_itinerary__imp_principal_port_slave_dis__geo_location__id");

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: formdata,
  redirect: 'follow'
};

fetch("https://voyages3-api.crc.rice.edu/voyage/aggroutes", requestOptions)
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.log('error', error));