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

    var state = {'clicked': false};
    var config;
    if (location.pathname.substring(1).includes("dash_board")) {
        setInterval(get_progress, 1000);
        set_session_functionality(state);
        var request = new XMLHttpRequest();
        request.open("POST", "/get_config", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'get_config'});

        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                config = JSON.parse(request.responseText);
                setSliders(config);
            }
        };
        request.send("jsonData=" + params);
    }
    if (location.pathname.substring(1).includes("results")) {
        var request = new XMLHttpRequest();
        request.open("POST", "/get_config", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'get_config'});

        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                config = JSON.parse(request.responseText);
                setEventSlider(config);
            }
        };
        request.send("jsonData=" + params);
    }

     if (location.pathname.substring(1).includes("admin_board")) {
        show_users_functionality();
     }


    $(document).on("click", "#load_tweets", function () {
        load_tweets(state);
    });
    $(document).on("click", "#create_topics", function () {
        create_topics(state);
    });
    $(document).on("click", "#merge_topics", function () {
        merge_topics(state);
    });
    $(document).on("click", "#show_events", function () {
        show_events(state);
    });

});

function show_users_functionality() {
    $("#show_users").on("click", function () {
        var request = new XMLHttpRequest();
        request.open("POST", "/show_users", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action': 'show_users'});
         request.onreadystatechange = function () {
             console.log(request.responseText);
             var responseJson = JSON.parse(request.responseText);
             var users = responseJson['users'];
              $("#sel2").empty();
              var nr_sessions = responseJson['nr_sessions'];
              var nr_topics = responseJson['nr_topics'];
              var nr_tweets = responseJson['nr_tweets'];
              $("#td_user").html(users[0]);
              $("#td_session").html(nr_sessions);
              $("#td_tweets").html(nr_tweets);
              $("#td_topics").html(nr_topics);

              $.each(users, function (index, value) {
                    $('<option>').text(value).appendTo($("#sel2"));
              });
         };
        request.send("jsonData=" + params);
    });
    $("#sel2").on('change', function() {
         var request = new XMLHttpRequest();
         request.open("POST", "/show_user_details", true);
         request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
         var user = this.value;
         request.onreadystatechange = function () {
              console.log(request.responseText);
              var responseJson = JSON.parse(request.responseText);
              var nr_sessions = responseJson['nr_sessions'];
              var nr_topics = responseJson['nr_topics'];
              var nr_tweets = responseJson['nr_tweets'];
              $("#td_user").html(user);
              $("#td_session").html(nr_sessions);
              $("#td_tweets").html(nr_tweets);
              $("#td_topics").html(nr_topics);
         };
         request.send("user=" + user);
    });
    $("#delete_user").on("click", function () {
        var request = new XMLHttpRequest();
         request.open("POST", "/delete_user", true);
         request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
         var user = $("#sel2").find(":selected").text();
          request.onreadystatechange = function () {
              console.log(request.responseText);
          };
         request.send("user=" + user);
    });

    $("#delete_user_data").on("click", function () {
        var request = new XMLHttpRequest();
         request.open("POST", "/delete_user_data", true);
         request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
         var user = $("#sel2").find(":selected").text();
          request.onreadystatechange = function () {
              console.log(request.responseText);
          };
         request.send("user=" + user);
    });

    $("#drop_all_tables").on("click", function () {
        var request = new XMLHttpRequest();
         request.open("POST", "/drop_all_tables", true);
         request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
         var user = $("#sel2").find(":selected").text();
          request.onreadystatechange = function () {
              console.log(request.responseText);
          };
         request.send("user=" + user);
    });



}

function set_session_functionality(state) {
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
            state['clicked'] = true;
            var action = {'action': 'delete', 'id': id};
            show_sessions(action);
            console.log(action);
            state['clicked'] = false;
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

function get_progress() {
    var request = new XMLHttpRequest();
    request.open("POST", "/get_progress", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            var progress = JSON.parse(request.responseText);
            $('.progress-bar').css('width', progress+'%');
            $('.progress-bar').html(progress+'%');

            if(progress == 100) {
                $('.progress-bar').removeClass("active");
            } else {
                $('.progress-bar').addClass("active");
            }
        }
    };
    request.send();
}


function show_events(state) {
    if (state['clicked'] == false) {
        var request = new XMLHttpRequest();
        request.open("POST", "/show_events", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
         var params = JSON.stringify({
            'granularity': $j("#slider-granularity").slider("value"),
            'session': $("#sel1").val()
        });
        state['clicked'] = true;
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                var result = JSON.parse(request.responseText);
                draw_graphs(result);
                state['clicked'] = false;
            }
        }
        request.send("jsonData=" + params);
    }
}
function merge_topics(state) {
    if (state['clicked'] == false) {
        var request = new XMLHttpRequest();
        request.open("POST", "/merge_topics", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({
            'merge_threshold': $j("#slider-threshold").slider("value"),
            'threads': $j("#slider-threads").slider("value"),
            'session': $("#sel1").val()
        });
        state['clicked'] = true;
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                state['clicked'] = false;
            }
        };
        request.send("jsonData=" + params);
    }
}

function draw_graphs(result) {
    console.log(result);
    var keys = Object.keys(result);
     $('.graphs').empty();
     $('.graphs').append('<div id="myCarousel" class="carousel" data-ride="carousel" data-interval="false">');

    $('#myCarousel').append('<div class="carousel-inner"></div>');
    $('#myCarousel').append('<ol class="carousel-indicators"></ol>');
    $('#myCarousel').append('<a class="left carousel-control" href="#myCarousel" data-slide="prev">'+
                            '<span class="glyphicon glyphicon-chevron-left"></span>'+
                            '<span class="sr-only">Previous</span>'+
                          '</a>'+
                          '<a class="right carousel-control" href="#myCarousel" data-slide="next">'+
                            '<span class="glyphicon glyphicon-chevron-right"></span>'+
                            '<span class="sr-only">Next</span>'+
                          '</a>');
     $('#myCarousel').carousel();

    var text = "";
    for (var i = 0, len = keys.length; i < len; i++) {

        if (i==0) {
             $('<div class="item graph active" id="graph'+i+'"></div>').appendTo('.carousel-inner');
             $('<li data-target="#myCarousel" data-slide-to="0" class="active"></li>').appendTo('.carousel-indicators');
        } else {
            $('<div class="item graph" id="graph'+i+'"></div>').appendTo('.carousel-inner');
            $('<li data-target="#myCarousel" data-slide-to="'+ i+'" class="active"></li>').appendTo('.carousel-indicators');
        }

         draw_graph(result[keys[i]], 'graph' + i);
    }


    console.log(text);
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
    console.log(id);
    Plotly.newPlot(document.getElementById(id), fig);
}

function create_topics(state) {
    if (state['clicked'] == false) {
        var request = new XMLHttpRequest();
        request.open("POST", "/create_topics", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({
            'nr_topics': $j("#slider-topics").slider("value"),
            'topic_words_nr': $j("#slider-words").slider("value"),
            'tweet_per_topic': $j("#slider-tweet_topic").slider("value"),
            'tweet_threshold': $j("#slider-tweet_threshold").slider("value"),
            'threads': $j("#slider-threads").slider("value"),
            'method': $('input[name=methods]:checked').val(),
            'session': $("#sel1").val()
        });
        state['clicked'] = true;
        request.onreadystatechange = function () {
            if (request.readyState == 4 && request.status == 200) {
                console.log(request.responseText);
                state['clicked'] = false;
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
        console.log("Calling load tweets");
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
                window.location.href = "/dash_board";
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
                window.location.href = "/dash_board";
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

     $j( "#slider-topics" ).slider({
     min: 1,
     max: 20,
     value: config['topics']['nr_topics'],
     step: 1,
     slide: function( event, ui ) {
     document.getElementById("slider-topics").parentNode.firstElementChild.innerHTML = "Topics per Interval: " + ui.value;
     }
     });
     document.getElementById("slider-topics").parentNode.firstElementChild.innerHTML =
     "Topics per Interval: " + $j( "#slider-topics" ).slider( "value");

     $j( "#slider-words" ).slider({
     min: 1,
     max: 10,
     value: config['topics']['topic_words_nr'],
     step: 1,
     slide: function( event, ui ) {
     document.getElementById("slider-words").parentNode.firstElementChild.innerHTML = "Words per Topic: " + ui.value;
     }
     });
     document.getElementById("slider-words").parentNode.firstElementChild.innerHTML =
     "Words per Topic: " + $j( "#slider-words" ).slider( "value");

     $j("#slider-tweet_topic").slider({
     min: 1,
     max: 10,
     value: config['topics']['tweet_per_topic'],
     step: 1,
     slide: function( event, ui ) {
     document.getElementById("slider-tweet_topic").parentNode.firstElementChild.innerHTML = "Words per Topic Membership: " + ui.value;
     }
     });
     document.getElementById("slider-tweet_topic").parentNode.firstElementChild.innerHTML =
     "Words per Topic Membership: " + $j( "#slider-tweet_topic" ).slider( "value");

     $j("#slider-tweet_threshold").slider({
     min: 0.001,
     max: 0.1,
     value: config['topics']['tweet_threshold'],
     step: 0.001,
     slide: function( event, ui ) {
     document.getElementById("slider-tweet_threshold").parentNode.firstElementChild.innerHTML = "Tweet Membership Threshold: " + ui.value;
     }
     });
     document.getElementById("slider-tweet_threshold").parentNode.firstElementChild.innerHTML =
     "Tweet Membership Threshold: " + $j( "#slider-tweet_threshold" ).slider( "value");


     $j( "#slider-threshold" ).slider({
     min: 0.01,
     max: 1,
     value:  config['events']['merge_threshold'],
     step: 0.01,
     slide: function( event, ui ) {
     document.getElementById("slider-threshold").parentNode.firstElementChild.innerHTML = "Topic Merging Threshold: " + ui.value;
     }
     });
     document.getElementById("slider-threshold").parentNode.firstElementChild.innerHTML =
     "Topic Merging Threshold: " + $j( "#slider-threshold" ).slider( "value");
}
function setEventSlider(config) {
     $j( "#slider-granularity" ).slider({
     min: 0.01,
     max: 1,
     value: config['events']['granularity'],
     step: 0.01,
     slide: function( event, ui ) {
     document.getElementById("slider-granularity").parentNode.firstElementChild.innerHTML = "Event Granularity: " + ui.value;
     }
     });
     document.getElementById("slider-granularity").parentNode.firstElementChild.innerHTML =
     "Event Granularity: " + $j( "#slider-granularity" ).slider( "value");

}