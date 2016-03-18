var ws;
init();

function init() {
    // Connect to Web Socket
    ws = new WebSocket(['ws://',window.location.hostname,':56625/'].join(''));

    // Set event handlers.
    ws.onopen = function() {
        output("onopen");
        var user_key = document.getElementById("user_key").value;
        ws.send(user_key);
    };

    ws.onmessage = function(e) {
        // e.data contains received string.
        output(e.data);
    };

    ws.onclose = function() {
        output("onclose");
        init();
    };

    ws.onerror = function(e) {
        output("onerror");
        console.log(e);
    };
}

function onSubmit() {
    var input = document.getElementById("input");
    // You can send message to the Web Socket using ws.send.
    ws.send(input.value);
    output("send: " + input.value);
    input.value = "";
    input.focus();
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
    list.scrollTop = list.scrollHeight;

    input.value="";

    return false;
}
