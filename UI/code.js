var recording = false;
var recognition;
var apigClient = apigClientFactory.newClient();

var params = {
    //This is where any header, path, or querystring request params go. The key is the parameter named as defined in the API
};

var additionalParams = {
    //If there are any unmodeled query parameters or headers that need to be sent with the request you can add them here
};

function searchImages(query){
   body["query"] = query
   apigClient.searchGet(params, body, additionalParams)
}



function uploadImage(event){

  var files = document.getElementById("imgfile").files;
  if (!files.length) {
    return alert("Please choose a file to upload first.");
  }
  var file = files[0];
  var fileName = file.name;

  body = file
  apigClient.photosPut(params, body, additionalParams)
}

function sendAudio(stream){
  console.log("I am here");
}

function audioSearch() {

    recording = true;
    audioProcess();
}

function audioProcess(){
  navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      .then(sendAudio);
}
