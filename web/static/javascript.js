$(document).ready(function () {
    $(document).on("click", "#login", function(){
        login_signup_show('login')
    });
    $(document).on("click", "#signup", function(){
        login_signup_show('signup')
    });

});

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
                window.location.href = "/";
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
                window.location.href = "/";
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