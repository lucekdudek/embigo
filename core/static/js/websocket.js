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
        if(e.data[0]=='l'){
            //alert(e.data);
            data = e.data.split(";");
            list = document.getElementById("users_list").getElementsByTagName("a");
            for (i = 0; i < list.length; i++) {
                found = false;
                for (j = 0; j < data.length; j++) {
                    if(data[j]==list[i].innerHTML){
                        list[i].parentNode.className = "users-list_item is-online";
                        found=true;
                        break;
                    }
                }
                if(!found)
                    list[i].parentNode.className = "users-list_item";
            }
        }else{
            output(e.data);
        }
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
    data = str.split(";",2);
    content = str.substring(data[0].length+data[1].length+2);
    var elem = document.createElement('li');
    elem.innerHTML = '<span class="communicator_author">' + data[1] + '</span>' + content;
    if(data[0] == "cu")
        elem.className = "communicator_sender";
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

    var username = document.getElementsByClassName("communicator")[0].getAttribute("data-username");

    var elem = document.createElement('li');
    elem.innerHTML = '<span class="communicator_author" title="TODO">' + username + '</span>' + input.value;
    elem.className = "communicator_sender";
    var list = document.getElementsByClassName("communicator_list")[0];
    list.appendChild(elem);
    scrollBottom();

    input.value="";

    return false;
}
