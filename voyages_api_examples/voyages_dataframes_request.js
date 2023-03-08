var myHeaders = new Headers();
myHeaders.append("Authorization", "Token XXXXXXXXXXXXX");

var formdata = new FormData();
formdata.append("selected_fields", "voyage_itinerary__imp_broad_region_voyage_begin__geo_location__name");
formdata.append("selected_fields", "voyage_slaves_numbers__imp_total_num_slaves_embarked");
formdata.append("cachename", "voyage_export");

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: formdata,
  redirect: 'follow'
};

fetch("https://voyages3-api.crc.rice.edu/voyage/caches", requestOptions)
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.log('error', error));