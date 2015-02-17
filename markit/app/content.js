/**
* Content javascript
* Watch for new page load and send url to background
*/

// watch recording tab and tell background if it changes
window.addEventListener("load", function() {
    // console.log("New url registered: "+window.location.href);
    chrome.runtime.sendMessage({
        type: "dom-loaded", 
        data: {
            url: window.location.href
        }
    }, function(response) {
    // console.log("BG status: "+ response.status);
    });
}, true);

// listen if we need to change windows
// chrome.runtime.onMessage.addListener( function(request, sender, sendResponse) {
// 	console.log("R: "+ request.action);
//   if (request.action == 'follow-link') {
//     window.location.href = request.link;
//   }
// });