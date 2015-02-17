/**
* Background script
* Keeps track of watch state: recording/not recording
* Keeps track of current path if recording
* Listens for url message from content.js on page load to record path
*/

var recording = {
	isRecording : false,
	path : [],

	toggle: function() {
		this.isRecording = !this.isRecording;
	},

	commitToPath : function(url) {
		if (this.isRecording) {
			// if url not in the path yet, add it to the end
			if(this.path.indexOf(url) == -1) 
				this.path.push(url);
			// else find last occurence and splice of the end (effectively reverting back) 
			else {
				var last = this.path.lastIndexOf(url);
				this.path.splice(last+1,this.path.length - last);
			}
		}
	},

	logPath: function() {
		console.log(this.path);
	},

	resetPath: function() {
		this.path = [];
	}


};

// listen for new url from content.js
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    switch(request.type) {
    	// commit to path
        case "dom-loaded":
            console.log("Received new URL: "+request.data.url);
            recording.commitToPath(request.data.url);
            sendResponse({status: "Current Path: "+recording.path,
        				  path: recording.path
        	});
        break;
        // turn recording on/off
        case "toggle-record":
        	recording.toggle();
			console.log("Recording? "+recording.isRecording);
        	sendResponse({status: recording.isRecording,
        				  path: recording.path
        	});
        break;
        case "is-recording":
        	sendResponse({status: recording.isRecording,
        				  path: recording.path
        	});
        break;
        case "reset-record":
        	recording.resetPath();
        	sendResponse({status: "Path reset!",
        				  path: recording.path
        	});
        break;
    }
    return true;
});