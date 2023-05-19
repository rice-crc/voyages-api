var myHeaders = new Headers();
myHeaders.append("Authorization", "Token XXXXXXXXXXXXX");

var formdata = new FormData();
formdata.append("hierarchical", "False");

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: formdata,
  redirect: 'follow'
};

fetch("https://voyages3-api.crc.rice.edu/voyage/", requestOptions)
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.log('error', error));