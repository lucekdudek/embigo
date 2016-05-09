var ws;
var conversations = new Array();
var username;
init();
scrollBottom();

function init() {
    if (typeof localStorage.current_conv === "undefined") {
        localStorage.current_conv = "";
    }
    connect();
    document.getElementById("close_btn").onclick = function () {
        var name = getConv();
        for (i in conversations) {
            if (conversations[i] == name) {
                conversations.splice(i, 1);
                changeConv(conversations[0]);
                localStorage.conversations = JSON.stringify(conversations);
                refreshList();
                break;
            }
        }
        document.getElementById("add_to_conversation").style.display="none";
    }

    document.getElementById("add_btn").onclick = function () {
        var elem=document.getElementById("add_to_conversation");
        if(elem.style.display=="none"){
            elem.style.display="block";
        }else{
            elem.style.display="none";
        }
    }

    window.addEventListener('storage', storageEventHandler, false);

    function storageEventHandler(evt) {
        if (evt.key == "conversations") {
            conversations = JSON.parse(localStorage.conversations);
            changeConv(conversations[0]);
            refreshList();
        } else if (evt.key == "current_conv") {
            list = document.getElementById("users_list").getElementsByTagName("a");
            for (i = 0; i < list.length; i++) {
                if (localStorage.current_conv == list[i].getAttribute("data-id")) {
                    changeConv(list[i].innerHTML);
                    break;
                }
            }
            list = document.getElementById("group_conv_list").getElementsByTagName("a");
            for (i = 0; i < list.length; i++) {
                if (localStorage.current_conv == list[i].getAttribute("data-id")) {
                    changeConv(list[i].innerHTML);
                    break;
                }
            }
        }
    }
}

function connect() {
    // Connect to Web Socket
    ws = new WebSocket(document.getElementsByClassName("communicator")[0].getAttribute("data-wsaddress"));

    // Set event handlers.
    ws.onopen = function () {
        //output("onopen");
        var user_key = document.getElementsByClassName("communicator")[0].getAttribute("data-port");
        ws.send(user_key);

        var space_users = document.getElementsByClassName("current-space_users")[0].getElementsByClassName("user-avatar");
        for (i = 0; i < space_users.length; i++) {
            space_users[i].onclick = function (){
                var username = this.getElementsByTagName("span")[0].innerHTML;
                ws.send("o;" + username);
            }
        }
    };

    ws.onmessage = function (e) {
        if (e.data[0] == 'o') { // isonline
            //alert(e.data);
            data = e.data.split(";");
            list = document.getElementById("users_list").getElementsByTagName("a");
            for (i = 0; i < list.length; i++) {
                found = false;
                for (j = 0; j < data.length; j++) {
                    if (data[j] == list[i].innerHTML) {
                        list[i].parentNode.className = "users-list_item is-online";
                        found = true;
                        break;
                    }
                }
                if (!found)
                    list[i].parentNode.className = "users-list_item";
            }
        } else if (e.data[0] == 'l') { //list of users
            var list = e.data.split(";");
            var el = document.getElementById("users_list");
            while (el.firstChild) {
                el.removeChild(el.firstChild);
            }
            for (i = 2; i < list.length; i += 2) {
                var li = document.createElement("li");
                var a = document.createElement("a");
                a.className = "users-list_item";
                a.href = "#";
                a.setAttribute("data-id", list[i - 1]);
                a.onclick = function () {
                    changeConv(this.innerHTML);
                    var found = false;
                    for (x in conversations) {
                        if (conversations[x] == this.innerHTML) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        conversations.push(this.innerHTML);
                        refreshList();
                    }
                    localStorage.conversations = JSON.stringify(conversations);
                    return false;
                }

                var text = document.createTextNode(list[i]);
                li.appendChild(a);
                a.appendChild(text);
                el.appendChild(li);
            }
        } else if (e.data[0] == 'L') { //list of group conversations
            var list = e.data.split(";");
            var el = document.getElementById("group_conv_list");
            while (el.firstChild) {
                el.removeChild(el.firstChild);
            }
            for (i = 2; i < list.length; i += 2) {
                var li = document.createElement("li");
                var a = document.createElement("a");
                a.className = "users-list_item";
                a.href = "#";
                a.setAttribute("data-id", list[i - 1]);
                a.onclick = function () {
                    changeConv(this.innerHTML);
                    var found = false;
                    for (x in conversations) {
                        if (conversations[x] == this.innerHTML) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        conversations.push(this.innerHTML);
                        refreshList();
                    }
                    localStorage.conversations = JSON.stringify(conversations);
                    return false;
                }

                var text = document.createTextNode(list[i]);
                li.appendChild(a);
                a.appendChild(text);
                el.appendChild(li);
            }
        } else if (e.data[0] == 'w') { // open chat window
            uname = e.data.substring(2);
            changeConv(uname);
            var found = false;
            for (x in conversations) {
                if (conversations[x] == uname) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                conversations.push(uname);
                refreshList();
            }
            localStorage.conversations = JSON.stringify(conversations);
        } else if (e.data[0] == 'a') { // list of messages
            data = e.data.split(";", 2); //data[1] - conversation id
            content = e.data.substring(data[0].length + data[1].length + 2);
            var json = JSON.parse(content);
            for (var i in json) {
                output(json[i]);
            }
        } else if (e.data[0] == 'u') { // get username
            username = e.data.substring(2);
            if (typeof localStorage.conversations !== "undefined") {
                conversations = JSON.parse(localStorage.conversations);
                changeConv(conversations[0]);
                refreshList();
            }
        } else {
            //TODO
            /*var id=e.data.split(";",2)[1];
             if(current_conv!=id){
             list = document.getElementById("users_list").getElementsByTagName("a");
             for (i = 0; i < list.length; i++) {
             if(id==list[i].getAttribute("data-id")){
             changeConv(list[i].innerHTML);
             conversations.push(list[i].innerHTML);
             alert("x");
             refreshList();
             break;
             }
             }
             }*/
            output(e.data); // text message
        }
    };

    ws.onclose = function () {
        //output("onclose");
        connect();
    };

    ws.onerror = function (e) {
        //output("onerror");
        console.log(e);
    };
}

function refreshList() {
    var conv_list = document.getElementById("communicator_users").getElementsByTagName("div");
    for (var nr = 0; nr < conv_list.length; nr++) {
        if (nr < conversations.length) {
            conv_list[nr].style.display = "block";
            conv_list[nr].getElementsByTagName("strong")[0].innerHTML = conversations[nr][0];
            conv_list[nr].setAttribute("data-name", conversations[nr]);

            conv_list[nr].onclick = function () {
                changeConv(this.getAttribute("data-name"));
            }
        } else {
            conv_list[nr].style.display = "none";
        }
    }
    if (conversations.length == 0) {
        document.getElementsByClassName("communicator")[0].style.display = "none";
        localStorage.current_conv = "";
    } else {
        document.getElementsByClassName("communicator")[0].style.display = "block";
    }
}

function changeConv(name) {
    document.getElementById("add_to_conversation").style.display="none";
    if (typeof name !== "undefined") {
        document.getElementById("conv-name").innerHTML = name;

        list = document.getElementById("users_list").getElementsByTagName("a");
        for (i = 0; i < list.length; i++) {
            if (name == list[i].innerHTML) {
                localStorage.current_conv = list[i].getAttribute("data-id");
                break;
            }
        }

        list = document.getElementById("group_conv_list").getElementsByTagName("a");
        for (i = 0; i < list.length; i++) {
            if (name == list[i].innerHTML) {
                localStorage.current_conv = list[i].getAttribute("data-id");
                break;
            }
        }

        clear();
        ws.send("n;" + name);
    }
}

function getConv() {
    return document.getElementById("conv-name").innerHTML;
}

function scrollBottom() {
    var list = document.getElementsByClassName("communicator_list")[0];
    list.scrollTop = list.scrollHeight;
}

function onCloseClick() {
    ws.close();
}

function clear() {
    document.getElementsByClassName("communicator_list")[0].innerHTML = "";
}

function output(str) {
    data = str.split(";", 3);
    if (data[1] == localStorage.current_conv) {
        content = str.substring(data[0].length + data[1].length + data[2].length + 3);
        var elem = document.createElement('li');
        elem.innerHTML = '<span class="communicator_author">' + data[2] + '</span>' + content;
        if (data[2] == username)
            elem.className = "communicator_sender";
        var list = document.getElementsByClassName("communicator_list")[0];
        list.appendChild(elem);
        list.scrollTop = list.scrollHeight;
    }
}

var formChat = document.getElementById("sendChat");

formChat.onsubmit = function () {
    input = document.getElementById("chatInput");
    input.focus();
    if (input.value == "") {
        return false;
    }

    var username = document.getElementsByClassName("communicator")[0].getAttribute("data-username");

    ws.send("m;" + getConv() + ";" + input.value);

    var elem = document.createElement('li');
    elem.innerHTML = '<span class="communicator_author" title="TODO">' + username + '</span>' + input.value;
    elem.className = "communicator_sender";
    var list = document.getElementsByClassName("communicator_list")[0];
    list.appendChild(elem);
    scrollBottom();

    input.value = "";

    return false;
}

var formAddUser = document.getElementById("add_to_conversation");

formAddUser.onsubmit = function () {
    ws.send("g;"+localStorage.current_conv+";"+this["users"].value);
    return false;
}