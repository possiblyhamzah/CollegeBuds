document.addEventListener('DOMContentLoaded', () => {

    
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    
    socket.on('connect', () => {

        
        document.querySelector('#send').onclick = () => {
            // const selection = document.getElementById("counter").text;
            // const e = document.getElementById("counter");
			// const selection = e.options[e.selectedIndex].text;
            const selection = document.querySelector('#counter').value;
            socket.emit('submit channel', {'selection': selection})
        };

        document.querySelector('#priv_send').onclick = () => {
            const selection = document.querySelector('#priv_counter').value;
            
            // const username = document.querySelector('#priv_username').value;
            socket.emit('submit priv channel', {'selection': selection})
        };
    });

    


    
    socket.on ('cast channel', data => {
        const li = document.createElement('li');

        
        li.innerHTML = `<a href="/chatroom/${data["chat_id"]}"> ${data["selection"]} </a>`;//li.innerHTML = `${data["selection"]}`;
        console.log(li.innerHTML);
        document.querySelector('#chatrooms').append(li);
    });

    socket.on ('cast priv channel', data => {
        const li = document.createElement('li');

        li.innerHTML = `<a href="/chatroom/${data["chat_id"]}"> ${data["selection"]} </a>`;//li.innerHTML = `${data["selection"]}`;
        console.log(li.innerHTML);
        document.querySelector('#chatrooms').append(li);
    });
});