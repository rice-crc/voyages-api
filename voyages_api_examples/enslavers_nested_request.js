var myHeaders = new Headers();
myHeaders.append("Authorization", "Token XXXXXXXXXXXXX");

var formdata = new FormData();

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  body: formdata,
  redirect: 'follow'
};

fetch("https://voyages3-api.crc.rice.edu/past/enslavers/", requestOptions)
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.log('error', error));