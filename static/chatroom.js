document.addEventListener('DOMContentLoaded', () => {

    const request = new XMLHttpRequest();
    request.open("POST", "/list");

   
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        localStorage.setItem("chat_id", data["chat_id"])
        let i;
        for ( i=0; i<data["message"].length; i++) {
            const li = document.createElement('li');
            const response = data["message"][i];

            li.innerHTML = `<div class = "post">${response["user_name"]} : ${response["selection"]} : ${response["time"]}</div>`;
            document.querySelector('#messages').append(li);
        }
    };
    request.send();
    


    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        document.querySelector('#send').onclick = function () {
            const selection = document.querySelector('#counter').value;
            socket.emit('submit message', {'selection': selection});
        };
    });

    socket.on ('cast message', data => {
        const li = document.createElement('li');

        li.innerHTML = `<div class = "post">${data["user_name"]} : ${data["selection"]} : ${data["time"]}</div>`;
        document.querySelector('#messages').append(li);
    });


});
