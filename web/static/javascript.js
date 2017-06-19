$(document).ready(function () {
    $(document).on("click", "#login", function(){
        login_signup_show('login');
    });
    $(document).on("click", "#signup", function(){
        login_signup_show('signup');
    });
    $(document).on("click", "#logout", function(){
        logout();
    });
    $(document).on("click", "#config", function(){
        window.location.href = "/config";
    });
     $(document).on("click", "#board", function(){
        window.location.href = "/board";
    });
    var config;
    if (location.pathname.substring(1).includes("config")) {
        var request = new XMLHttpRequest();
        request.open("POST", "/get_config", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        var params = JSON.stringify({'action' : 'get_config'});

        request.onreadystatechange = function() {
            if (request.readyState == 4 && request.status == 200) {
               config = JSON.parse(request.responseText);
               setSliders(config);
               setDatabaseInputFields(config);
            }
       }
       request.send("jsonData="+params);
    };
     $(document).on("click", "#load_tweets", function(){
        load_tweets();
    });

});

function load_tweets() {
   var form_data = new FormData($('#board_form')[0]);
    $.ajax({
        type: 'POST',
        url: '/load_tweets',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
            console.log('Success!');
            $("#load_tweets_icon").text("Incarc");
        },
    });

}

function send_config_update(config) {
    config['topics']['granularity'] = $( "#slider-granularity" ).slider( "value");
    config['topics']['merge_threshold'] = $( "#slider-threshold" ).slider( "value");
    config['topics']['topic_words_nr'] =  $( "#slider-words" ).slider( "value");
    config['topics']['nr_topics'] =  $( "#slider-topics" ).slider( "value");
    config['general']['batch_size'] = $( "#slider-batch" ).slider( "value");
    config['general']['concurrent_tasks'] = $( "#slider-threads" ).slider( "value");
    config['database']['host'] =  $("#host").val();
    config['database']['port'] =  $("#port").val();
    config['database']['db'] =  $("#db").val();
     var request = new XMLHttpRequest();
    request.open("POST", "/set_config", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify(config);
    request.send("jsonData="+params);

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
    var params = JSON.stringify({'action' : 'config'});

     request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            configJson = JSON.parse(request.responseText);
            console.log(configJson['user']);

        }
   }

    request.send("jsonData="+params);
}

function logout() {
    var request = new XMLHttpRequest();

    request.open("POST", "/logout", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action' : 'logout'});

   request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            if (request.responseText=="ok") {
                 window.location.href = "/";
            }
        }
   }

    request.send("jsonData="+params);
}

function login() {
    $("#error_message").html("");
    id = $("#id").val();
    password = $("#password").val();

    if (id =="" || password=="") {
        $("#error_message").html("please complete all fields")
        $("#error_message").css("visibility", "visible");
        return;
    }
    var request = new XMLHttpRequest();

    request.open("POST", "/check_credentials", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var form = $(".login_form").serializeArray();
    var params = JSON.stringify({'action' : 'login', 'form': form });

    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            if (request.responseText=="ok") {
                 window.location.href = "/board";
            } else {
                 $("#error_message").html("Log In failed")
                $("#error_message").css("visibility", "visible");
                $("#id").val("");
                $("#password").val("");
            }
        }
    };

    request.send("jsonData="+params);
}

function signup() {
    $("#error_message").html("");
    password = $("#password").val();
    confirm_password = $("#confirm_password").val();
    if (password != confirm_password) {
        $("#error_message").html("passwords are not identical")
        $("#error_message").css("visibility", "visible");
        return;
    }

    signup_email = $("#signup_email").val();
    signup_username = $("#signup_username").val();

    if (signup_email =="" || signup_username=="" || password=="") {
        $("#error_message").html("please complete all fields")
        $("#error_message").css("visibility", "visible");
        return;
    }
    var request = new XMLHttpRequest();
    var form = $(".signup_form").serializeArray();

    request.open("POST", "/check_credentials", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action' : 'signup','form': form});
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            console.log(request.responseText);
            if (request.responseText=="ok") {
                window.location.href = "/board";
            } else {
                 $("#error_message").html("Sign up failed")
                $("#error_message").css("visibility", "visible");
                $("#signup_email").val("");
                $("#password").val("");
                $("#confirm_password").val("");
                $("#signup_username").val("");
            }
        }
    };
    request.send("jsonData="+params);
}
function login_signup_show(message) {

    var request = new XMLHttpRequest();

    request.open("POST", "/", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var params = JSON.stringify({'action' : message });

    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
           $(".main").html(request.responseText);
        }
    };
    request.send("jsonData="+params);
}

function uploadFile(target) {
    var file = target.files[0].name;
    document.getElementById("file").innerHTML = target.files[0].name;
}
function setSliders(config) {

     $( "#slider-threads" ).slider({
          min: 1,
          max: 16,
          value: config['general']['concurrent_tasks'],
          step: 1,
          slide: function( event, ui ) {
              document.getElementById("slider-threads").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
          }
    });
    document.getElementById("slider-threads").parentNode.firstElementChild.innerHTML =
                "Value: " + $( "#slider-threads" ).slider( "value");

     $( "#slider-batch" ).slider({
          min: 50000,
          max: 500000,
          value: config['general']['batch_size'],
          step: 50000,
          slide: function( event, ui ) {
              document.getElementById("slider-batch").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
          }
    });
     document.getElementById("slider-batch").parentNode.firstElementChild.innerHTML =
                "Value: " + $( "#slider-batch" ).slider( "value");

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
          value:  config['topics']['merge_threshold'],
          step: 0.1,
          slide: function( event, ui ) {
              document.getElementById("slider-threshold").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
          }
    });
    document.getElementById("slider-threshold").parentNode.firstElementChild.innerHTML =
                "Value: " + $( "#slider-threshold" ).slider( "value");

     $( "#slider-granularity" ).slider({
          min: 0.1,
          max: 1,
          value: config['topics']['granularity'],
          step: 0.1,
          slide: function( event, ui ) {
              document.getElementById("slider-granularity").parentNode.firstElementChild.innerHTML = "Value: " + ui.value;
          }
    });
    document.getElementById("slider-granularity").parentNode.firstElementChild.innerHTML =
                "Value: " + $( "#slider-granularity" ).slider( "value");
}
