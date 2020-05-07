try {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();
}
catch(e) {
  console.error(e);
  $('.no-browser-support').show();
  $('.app').hide();
 };


var recording = false;
var recognition;
var apigClient = apigClientFactory.newClient();


function audioProcessing(){
	document.getElementById('query').value = null;
	let final_transcript = '';
	if (recording == false){
		recognition.start();
		recording = true;
  		console.log('Started voice recognition');
  	 	recognition.onresult = function(event) {
	    	var interim_transcript = '';

	    	for (var i = event.resultIndex; i < event.results.length; ++i) {
		      if (event.results[i].isFinal) {
		        final_transcript += event.results[i][0].transcript;
		      } else {
		        interim_transcript += event.results[i][0].transcript;
		      }
		    }
		    recording = false;
		    console.log("Output:",final_transcript);
		    document.getElementById("displayImages").innerHTML = null;
  			document.getElementById("uploadResponse").innerHTML = null;
		    searchImages(final_transcript);
		    console.log("Debug")
		}

		recognition.onspeechend = function() {
		  searchErrorResponse.innerHTML = 'You were quiet for a while so voice recognition turned itself off.';
		}

		recognition.onerror = function(event) {
		  if(event.error == 'no-speech') {
		    searchErrorResponse.innerHTML = 'No speech was detected. Try again.';  
		  };
    	}
    }
  	else{
  		recognition.stop();
  		recording = false;
  	};
};