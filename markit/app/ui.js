/* UI script
* Tell background if we've recorded or not
*/
var p; //path div

// When the popup HTML has loaded
window.addEventListener('load', function() {
  // run on page load, add event listeners to UI according to extensions security protocols
  document.getElementById("record").addEventListener('click', function() {
    chrome.runtime.sendMessage({
      type: "toggle-record", 
    }, function(response) {
      console.log("Recording? "+ response.status);
      if (response.status) document.getElementById("recording").innerHTML = "Recording: Yes";
      else document.getElementById("recording").innerHTML = "Recording: No";
      updatePath(response.path);
    });
  });
  document.getElementById("cancel").addEventListener('click', function() {
    chrome.runtime.sendMessage({
        type: "reset-record", 
    }, function(response) {
      console.log(response.status);
      updatePath(response.path);
    });
  });
  // document.getElementById("save").addEventListener('click', savePath(path));

  // make sure "Recording:" is correct
  chrome.runtime.sendMessage({
    type: "is-recording",
  }, function(response) {
      if (response.status) document.getElementById("recording").innerHTML = "Recording: Yes";
      else document.getElementById("recording").innerHTML = "Recording: No";
      updatePath(response.path);
  });

  // grab the path div
  p = document.getElementById("path");
});

// update the current path display
function updatePath(currentPath) {
  var html = "<p>Current Path:<br>[";
  // console.log(currentPath);
  for(var i=0; i<currentPath.length; i++) {
    var url = currentPath[i];
    // console.log(url);
    // append a new p for wach url, skip the trailing ',' on the last one
    i == currentPath.length-1 ?
      html += "<br><a>"+url.substring(0,40)+"</a>" :
      html += "<br><a>"+url.substring(0,40)+"</a>,";
      // html += "<br><a href='"+url+"' class='path'>"+url.substring(0,40)+"</a>" :
      // html += "<br><a href='"+url+"' class='path'>"+url.substring(0,40)+"</a>,";
  }
  html += "<br>]</p>";
  p.innerHTML = html;

  /**********
  * Set up download current path button
  **********/
  // var counter = 1;
  // if (StorageArea.get("counter")) {
  //   counter = StorageArea.get("counter");
  // }
  var path = {'path':currentPath};
  console.log('CPath: '+ currentPath);

  var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(path));
  console.log('Data: '+ data);
  saveLink = document.getElementById('save');
  saveLink.setAttribute("href","data:" + data);
  saveLink.setAttribute("download", "path_data.json");

}

