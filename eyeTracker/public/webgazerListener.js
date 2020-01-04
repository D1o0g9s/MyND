var connection = new WebSocket('ws://localhost:8765');
var prevPrediction = null; // to keep track of the previous location

let calibrationInstr1 = "1. Align face into the square and make sure the green outline is apt.";
let calibrationInstr2 = "2. Concentrate your eyes on the cursor."; 
let calibrationInstr3 = "3. Click on the webpage in various locations to calibrate. ";

let instructions = "Hi, welcome to eye tracker!\n" 
    + "After dismissing this message by clicking 'ok', set up the eye tracker by:\n" 
    + calibrationInstr1 + "\n"
    + calibrationInstr2 + "\n"
    + calibrationInstr3; 


function euclideanDistance(p,p2){
    xdiff = Math.pow((p.x-p2.x),2);
    ydiff = Math.pow((p.y-p2.y),2);
   return Math.sqrt( xdiff + ydiff)
}

function averageLocation(p, p2){ 
    x = Math.floor(p.x / 2) + Math.floor(p2.x / 2)
    y = Math.floor(p.y / 2) + Math.floor(p2.y / 2)
    return {"x": x, "y": y}
}

connection.onopen = function () {
    connection.send('Ping'); // Send the message 'Ping' to the server

    // Update the xPrediction and yPrediction values 
    var xPred = document.getElementById("xPred");
    xPred.innerHTML = calibrationInstr1;
    var yPred = document.getElementById("yPred");
    yPred.innerHTML = calibrationInstr2;
    var normValue = document.getElementById("normValue");
    normValue.innerHTML = calibrationInstr3;

    // Create a webgazer listener 
    webgazer.begin() 
    webgazer.setGazeListener(function(data, elapsedTime) {
        if (data == null) {
            return;
        }
        
        var xprediction = data.x; //these x coordinates are relative to the viewport
        var yprediction = data.y; //these y coordinates are relative to the viewport
        var eyeLocation = {"x": parseInt(xprediction), "y":parseInt(yprediction), "quadrant":"center"};

        // Check the distance from previous eye location to this eye location
        if (prevPrediction != null){
            eyeLocation = averageLocation(prevPrediction, eyeLocation)
        }
        prevPrediction = eyeLocation

        // Update the eye cursor location
        var circle = document.getElementById("eyeCursor");
        

        if (eyeLocation.x > (window.innerWidth / 3) && eyeLocation.x < (2* window.innerWidth / 3) ) {
            circle.setAttribute("fill","red");
        } else {
            circle.setAttribute("fill","red");
        }

        eyeLocation["x_norm"] = eyeLocation.x / window.innerWidth; 
        eyeLocation["y_norm"] = eyeLocation.y / window.innerHeight; 

        circle.setAttribute("cx",eyeLocation.x);
        circle.setAttribute("cy",eyeLocation.y);
        
        // Update the xPrediction and yPrediction values 
        var xPred = document.getElementById("xPred");
        xPred.innerHTML = "xPred: " + xprediction;
        var yPred = document.getElementById("yPred");
        yPred.innerHTML = "yPred: " + yprediction;
        var normValue = document.getElementById("normValue");
        normValue.innerHTML = "X normValue: " + eyeLocation["x_norm"]


        // Send through websocket 
        eyeLocationString = JSON.stringify(eyeLocation);
        connection.send(eyeLocationString);

    }).begin();

    alert(instructions);
};

window.onbeforeunload = function() {
    connection.onclose = function () {}; // disable onclose handler first
    connection.close();
    //webgazer.end(); //Uncomment if you want to save the data even if you reload the page.
    window.localStorage.clear(); //Comment out if you want to save data across different sessions
}; 