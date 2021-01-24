// Create WebSocket connection.
const apiGSocket = new WebSocket('wss://8lxphbfn9a.execute-api.eu-west-2.amazonaws.com/production');
apiGSocket.onmessage = function(evt) {onMessageReceived(evt)};

let connectionId = undefined;


var albumBucketName = "celebritylookalike";
var bucketRegion = "eu-west-2";
var IdentityPoolId = "eu-west-2:dec13ae8-f00e-4b1a-a58d-d4bcd53b07e5";

AWS.config.update({
    region: bucketRegion,
    credentials: new AWS.CognitoIdentityCredentials({
        IdentityPoolId: IdentityPoolId
    })
});

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

async function uploadPhoto() {
    document.getElementById('response').innerHTML = "Uploading...";
    var files = document.getElementById("photoupload").files;
    if (!files.length) {
        alert("Please choose a file to upload first.");
    }
    var file = files[0];
    if (!file.type.match('image.*')) {
        alert('Unknown format');
    }

    var fileName = 'upload/' + uuidv4() + file.name;

    const res = await axios({
        url: 'https://rllzdt898b.execute-api.eu-west-2.amazonaws.com/prod/presignedurl',
        method: 'post',
        data: {'key': fileName}
    });

    console.log(res);
    fetch(res.uploadURL, {
        method: 'PUT',
        body: file
    }).then(res => {
        console.log('Result: ', res)
        console.log(fileName);
        sendS3Key(fileName);
        document.getElementById('response').innerHTML = "Uploaded photo! Working...";
    });
}

function sendS3Key(key) {
    apiGSocket.send(JSON.stringify({"action": "submitJob", "key": key}))
}

function onMessageReceived(payload) {
    var message = JSON.parse(payload.data);
    console.log(message);

    if (message.action === 'connected') {
        connectionId = message.connectionId;
        console.log(`Received connection id: ${connectionId}`)
    } else if (message.action === 'jobfinished') {
        console.log(`Got response from backend ${message.response}`)
        var biden = message.response.biden;
        var trump = message.response.trump;
        var faces = message.response.faces;
        var result = ''
        if (faces) {
            if (biden && trump) {
                result = 'This is a picture of both Donald Trump and Joe Biden!'
            } else if (biden) {
                result = 'This is a picture of Joe Biden!'
            } else if (trump) {
                result = 'This is a picture of Donald Trump!'
            } else {
                result = 'This is not a picture of Joe Biden, nor Donald Trump!'
            }
        } else {
            result = 'There are no faces on this picture!'
        }
        document.getElementById('response').innerHTML = `Result: ${result}`;
    }
}
