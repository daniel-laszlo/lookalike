
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

function uploadPhoto() {
    document.getElementById('response').innerHTML = "Uploading...";
    var files = document.getElementById("photoupload").files;
    if (!files.length) {
        return alert("Please choose a file to upload first.");
    }
    var file = files[0];
    if (!file.type.match('image.*')) {
        alert('Unknown format');
    }

    var fileName = uuidv4() + file.name;

    // Use S3 ManagedUpload class as it supports multipart uploads
    var upload = new AWS.S3.ManagedUpload({
        params: {
            Bucket: albumBucketName,
            Key: "upload/" + fileName,
            Body: file,
            ACL: "public-read",
        }
    });

    var promise = upload.promise();

    promise.then(
        function(data) {
            console.log(data.key);
            sendS3Key(data.key);
            document.getElementById('response').innerHTML = "Uploaded photo! Working...";
        },
        function(err) {
            return alert("There was an error uploading your photo: ", err.message);
        }
    );
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
    }
    if (message.action === 'jobfinished') {
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
