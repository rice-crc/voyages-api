var myHeaders = new Headers();
myHeaders.append("Authorization", "Token XXXXXXXXXXXXX");

var formdata = new FormData();
formdata.append("aggregate_fields", "voyage_slaves_numbers__imp_total_num_slaves_embarked");
formdata.append("aggregate_fields", "voyage_slaves_numbers__imp_total_num_slaves_disembarked");
formdata.append("aggregate_fields", "voyage_dates__imp_arrival_at_port_of_dis_yyyy");

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: formdata,
  redirect: 'follow'
};

fetch("https://voyages3-api.crc.rice.edu/voyage/aggregations", requestOptions)
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.log('error', error));