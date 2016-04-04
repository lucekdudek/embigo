var ws;
init();
scrollBottom();

function init() {
    // Connect to Web Socket
    ws = new WebSocket(document.getElementsByClassName("communicator")[0].getAttribute("data-wsaddress"));

    // Set event handlers.
    ws.onopen = function() {
        //output("onopen");
        var user_key = document.getElementsByClassName("communicator")[0].getAttribute("data-port");
        ws.send(user_key);
    };

    ws.onmessage = function(e) {
        // e.data contains received string.
        output(e.data);
    };

    ws.onclose = function() {
        //output("onclose");
        init();
    };

    ws.onerror = function(e) {
        //output("onerror");
        console.log(e);
    };
}

function scrollBottom() {
    var list = document.getElementsByClassName("communicator_list")[0];
    list.scrollTop = list.scrollHeight;
}

function onCloseClick() {
    ws.close();
}

function output(str) {
    var elem = document.createElement('li');
    elem.innerHTML = str;
    //elem.className = "communicator_sender";
    var list = document.getElementsByClassName("communicator_list")[0];
    list.appendChild(elem);
    list.scrollTop = list.scrollHeight;
}

var formChat = document.getElementById("sendChat");

formChat.onsubmit = function(){
    input = document.getElementById("chatInput");
    input.focus();
    if(input.value == ""){
        return false;
    }
    ws.send(input.value);

    var elem = document.createElement('li');
    elem.innerHTML = input.value;
    elem.className = "communicator_sender";
    var list = document.getElementsByClassName("communicator_list")[0];
    list.appendChild(elem);
    scrollBottom();

    input.value="";

    return false;
}
