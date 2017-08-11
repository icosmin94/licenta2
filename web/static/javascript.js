var $j = jQuery.noConflict(true);
console.log($().jquery);
console.log($j().jquery);

$(document).ready(function () {

    $(document).on("click", "#login", function () {
        event.preventDefault();
        login_signup_show('login');
    });
    $(document).on("click", "#signup", function () {
        event.preventDefault();
        login_signup_show('signup');
    });

    $(document).on("click", "#logout", function () {
        logout();
    });
    $(document).on("click", "#config", function () {
        window.location.href = "/config";
    });
    $(document).on("click", "#username", function () {
        event.preventDefault();
    });

    $(".nav a").on("click", function () {
        $(".nav").find(".active").removeClass("active");
        $(this).parent().addClass("active");
    });
    var action = {'action': 'show'};
    show_sessions(action);

    var config;
    if (location.pathname.substring(1).includes("board")) {
        set_session_functionality();
        var request = new XMLHttpRequest();
        request.open("POST", "/get_config", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'get_config'});

        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                config = JSON.parse(request.responseText);
                setSliders(config);
                // setDatabaseInputFields(config);
            }
        }
        request.send("jsonData=" + params);
    }
    ;
    /*    $(document).on("click", "#config_button", function(){
     config = send_config_update(config);
     window.location.href = "/board";
     });*/

    var state = {'clicked': false};
    $(document).on("click", "#load_tweets", function () {
        load_tweets(state);
    });
    $(document).on("click", "#create_topics", function () {
        create_topics(state);
    });
    $(document).on("click", "#process_events", function () {
        process_events(state);
    });
    $(document).on("click", "#show_events", function () {
        show_events(state);
    });

});

function set_session_functionality() {
    $("#create_session").on("click", function () {
        var request = new XMLHttpRequest();
        request.open("POST", "/create_session", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'create_new_session'});
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                var sessions = JSON.parse(request.responseText)['sessions'];
                console.log(sessions);
                $("#sel1").empty();
                $.each(sessions, function (index, value) {
                    $('<option>').text(value).appendTo($("#sel1"));
                });
            }
        }
        request.send("jsonData=" + params);
    });
    $("#delete_session").on("click", function () {
        var id = $('#sel1').find(":selected").text();
        if (id != '') {
            var action = {'action': 'delete', 'id': id};
            show_sessions(action);
            console.log(action);
        }
    });
}

function show_sessions(action) {
    var request = new XMLHttpRequest();
    request.open("POST", "/show_session", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = null;
    if (action['action'] == 'show') {
        params = JSON.stringify({'action': 'show_session'});
    } else {
        params = JSON.stringify({'action': 'delete', 'id': action['id']});
    }

    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            var sessions = JSON.parse(request.responseText)['sessions'];
            console.log(sessions);
            $("#sel1").empty();
            $.each(sessions, function (index, value) {
                $('<option>').text(value).appendTo($("#sel1"));
            });
        }
    }
    request.send("jsonData=" + params);
}


function show_events(state) {
    if (state['clicked'] == false) {
        var request = new XMLHttpRequest();
        request.open("POST", "/show_events", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'show_events'});
        $("#show_events_icon").css("visibility", "visible");
        state['clicked'] = true;
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                var result = JSON.parse(request.responseText);
                draw_graphs(result);
                state['clicked'] = false;
                $("#show_events_icon").css("visibility", "hidden");
            }
        }
        request.send("jsonData=" + params);
    }
}
function process_events(state) {
    if (state['clicked'] == false) {
        var request = new XMLHttpRequest();
        request.open("POST", "/process_events", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'process_events'});
        $("#process_events_icon").css("visibility", "visible");
        state['clicked'] = true;
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                state['clicked'] = false;
                $("#process_events_icon").css("visibility", "hidden");
            }
        }
        request.send("jsonData=" + params);
    }
}

function draw_graphs(result) {
    console.log(result);
    var keys = Object.keys(result);
    for (var i = 0, len = keys.length; i < len; i++) {
        console.log(keys[i]);
        $('.graphs').append('<div class="graph" id="graph' + i + '"></div>');
        draw_graph(result[i], 'graph' + i);
    }
}

function draw_graph(event, id) {
    var trace = {
        x: event['x'],
        y: event['y'],
        mode: 'lines+markers',
        name: 'Tweets/Hour'
    };
    var data = [trace];
    var x_axis_template = {
        showgrid: true,
        zeroline: false,
        nticks: event['x'].length,
        showline: false,
        title: 'Time',
        mirror: 'all'
    };
    var y_axis_template = {
        showgrid: true,
        zeroline: true,
        nticks: 10,
        showline: false,
        title: 'Tweets',
        mirror: 'all'
    };
    var layout = {
        showlegend: true,
        xaxis: x_axis_template,
        yaxis: y_axis_template,
        title: event['title'],
        titlefont: {
            size: 12
        },
    };
    var fig = {
        data: data,
        layout: layout
    };

    Plotly.newPlot(document.getElementById(id), fig);
}

function create_topics(state) {
    if (state['clicked'] == false) {
        var request = new XMLHttpRequest();
        request.open("POST", "/create_topics", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'create_topics'});
        $("#create_topics_icon").css("visibility", "visible");
        state['clicked'] = true;
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                console.log(request.responseText)
                state['clicked'] = false;
                $("#create_topics_icon").css("visibility", "hidden");
            }
        }
        request.send("jsonData=" + params);
    }
}
function load_tweets(state) {
    if (state['clicked'] == false && $("#sel1").val() != "") {
        var form_data = new FormData($('#board_form')[0]);
        var params = JSON.stringify({
            'threads': $j("#slider-threads").slider("value"),
            'batch': $j("#slider-batch").slider("value"),
            'session': $("#sel1").val()
        });
        form_data.append('jsonData', params);
        state['clicked'] = true;
        $.ajax({
            type: 'POST',
            url: '/load_tweets',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                console.log(data);
                state['clicked'] = false;
            },
        });
    }
}

function send_config_update(config) {
    config['topics']['tweet_per_topic'] = $("#slider-tweet_topic").slider("value");
    config['topics']['tweet_threshold'] = $("#slider-tweet_threshold").slider("value");
    config['events']['granularity'] = $("#slider-granularity").slider("value");
    config['events']['merge_threshold'] = $("#slider-threshold").slider("value");
    config['topics']['topic_words_nr'] = $("#slider-words").slider("value");
    config['topics']['nr_topics'] = $("#slider-topics").slider("value");
    config['general']['batch_size'] = $("#slider-batch").slider("value");
    config['general']['concurrent_tasks'] = $("#slider-threads").slider("value");
    config['database']['host'] = $("#host").val();
    config['database']['port'] = $("#port").val();
    config['database']['db'] = $("#db").val();
    var request = new XMLHttpRequest();
    request.open("POST", "/set_config", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify(config);
    request.send("jsonData=" + params);

    return config;

}
function setDatabaseInputFields(config) {
    $("#host").val(config['database']['host']);
    $("#port").val(config['database']['port']);
    $("#db").val(config['database']['db']);
}
function config() {
    var request = new XMLHttpRequest();

    request.open("POST", "/config", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action': 'config'});

    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            configJson = JSON.parse(request.responseText);
            console.log(configJson['user']);

        }
    }

    request.send("jsonData=" + params);
}

function logout() {
    var request = new XMLHttpRequest();

    request.open("POST", "/logout", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action': 'logout'});

    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            if (request.responseText == "ok") {
                window.location.href = "/";
            }
        }
    }

    request.send("jsonData=" + params);
}

function login() {
    $("#error_message").html("");
    id = $("#id").val();
    password = $("#password").val();

    if (id == "" || password == "") {
        $("#error_message").html("<strong>Error ! </strong> Please complete both fields")
        $("#error_message").css("visibility", "visible");
        return;
    }
    var request = new XMLHttpRequest();

    request.open("POST", "/check_credentials", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var form = $("#login_form").serializeArray();
    var params = JSON.stringify({'action': 'login', 'form': form});

    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            if (request.responseText == "ok") {
                window.location.href = "/board";
            } else {
                $("#error_message").html("<strong>Error ! </strong> Incorrect Username or Password")
                $("#error_message").css("visibility", "visible");
                $("#id").val("");
                $("#password").val("");
            }
        }
    };

    request.send("jsonData=" + params);
}

function signup() {
    $("#error_message").html("");
    password = $("#password").val();
    confirm_password = $("#confirm_password").val();
    if (password != confirm_password) {
        $("#error_message").html("<strong>Error ! </strong> Passwords are not identical")
        $("#error_message").css("visibility", "visible");
        return;
    }

    signup_email = $("#signup_email").val();
    signup_username = $("#signup_username").val();

    if (signup_email == "" || signup_username == "" || password == "") {
        $("#error_message").html("<strong>Error ! </strong> Please complete all fields")
        $("#error_message").css("visibility", "visible");
        return;
    }
    var request = new XMLHttpRequest();
    var form = $("#signup_form").serializeArray();

    request.open("POST", "/check_credentials", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action': 'signup', 'form': form});
    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            if (request.responseText == "ok") {
                window.location.href = "/board";
            } else {
                $("#error_message").html("<strong>Error ! </strong> Sign Up failed. Username or email already exists")
                $("#error_message").css("visibility", "visible");
                $("#signup_email").val("");
                $("#password").val("");
                $("#confirm_password").val("");
                $("#signup_username").val("");
            }
        }
    };
    request.send("jsonData=" + params);
}
function login_signup_show(message) {

    var request = new XMLHttpRequest();

    request.open("POST", "/", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action': message});

    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            $(".main").html(request.responseText);
        }
    };
    request.send("jsonData=" + params);
}

function uploadFile(target) {
    var file = target.files[0].name;
    document.getElementById("file").innerHTML = target.files[0].name;
}
function setSliders(config) {

    $j("#slider-threads").slider({
        min: 1,
        max: 16,
        value: config['tweets']['threads_number'],
        step: 1,
        slide: function (event, ui) {
            document.getElementById("slider-threads").parentNode.firstElementChild.innerHTML = "Threads Number: " + ui.value;
        }
    });
    document.getElementById("slider-threads").parentNode.firstElementChild.innerHTML =
        "Threads Number: " + $j("#slider-threads").slider("value");

    $j("#slider-batch").slider({
        min: 50000,
        max: 500000,
        value: config['tweets']['batch_size'],
        step: 50000,
        slide: function (event, ui) {
            document.getElementById("slider-batch").parentNode.firstElementChild.innerHTML = "Batch Size: " + ui.value;
        }
    });
    document.getElementById("slider-batch").parentNode.firstElementChild.innerHTML =
        "Batch Size: " + $j("#slider-batch").slider("value");
    /*
     $( "#slider-topics" ).slider({
     min: 1,
     max: 20,
     value: config['topics']['nr_topics'],
     step: 1,
     slide: function( event, ui ) {
     document.getElementById("slider-topics").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
     }
     });
     document.getElementById("slider-topics").parentNode.firstElementChild.innerHTML =
     "Value: " + $( "#slider-topics" ).slider( "value");

     $( "#slider-words" ).slider({
     min: 1,
     max: 10,
     value: config['topics']['topic_words_nr'],
     step: 1,
     slide: function( event, ui ) {
     document.getElementById("slider-words").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
     }
     });
     document.getElementById("slider-words").parentNode.firstElementChild.innerHTML =
     "Value: " + $( "#slider-words" ).slider( "value");

     $( "#slider-threshold" ).slider({
     min: 0.1,
     max: 1,
     value:  config['events']['merge_threshold'],
     step: 0.1,
     slide: function( event, ui ) {
     document.getElementById("slider-threshold").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
     }
     });
     document.getElementById("slider-threshold").parentNode.firstElementChild.innerHTML =
     "Value: " + $( "#slider-threshold" ).slider( "value");

     $( "#slider-granularity" ).slider({
     min: 0.05,
     max: 1,
     value: config['events']['granularity'],
     step: 0.05,
     slide: function( event, ui ) {
     document.getElementById("slider-granularity").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
     }
     });
     document.getElementById("slider-granularity").parentNode.firstElementChild.innerHTML =
     "Value: " + $( "#slider-granularity" ).slider( "value");

     $("#slider-tweet_topic").slider({
     min: 1,
     max: 10,
     value: config['topics']['tweet_per_topic'],
     step: 1,
     slide: function( event, ui ) {
     document.getElementById("slider-tweet_topic").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
     }
     });
     document.getElementById("slider-tweet_topic").parentNode.firstElementChild.innerHTML =
     "Value: " + $( "#slider-tweet_topic" ).slider( "value");

     $("#slider-tweet_threshold").slider({
     min: 0.001,
     max: 0.1,
     value: config['topics']['tweet_threshold'],
     step: 0.001,
     slide: function( event, ui ) {
     document.getElementById("slider-tweet_threshold").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
     }
     });
     document.getElementById("slider-tweet_threshold").parentNode.firstElementChild.innerHTML =
     "Value: " + $( "#slider-tweet_threshold" ).slider( "value");*/
}
