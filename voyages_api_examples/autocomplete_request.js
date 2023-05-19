var myHeaders = new Headers();
myHeaders.append("Authorization", "Token XXXXXXXXXXXXX");

var formdata = new FormData();
formdata.append("voyage_itinerary__imp_broad_region_voyage_begin__geo_location__name", "af");

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: formdata,
  redirect: 'follow'
};

fetch("https://voyages3-api.crc.rice.edu/voyage/autocomplete", requestOptions)
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.log('error', error));