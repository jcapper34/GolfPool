/*
FOR LOGIN
 */
function submit_login() {
    let button = $("#submit-button");
    const email = $("#login-email").val();
    const pin = $("#login-pin").val();

    if((email === "") || (pin === "") ) {
        window.alert("Please complete form before submitting");
        return;
    }
    button.addClass('is-loading');
    $.ajax({
        url: "/picks/change/submit-login",
        method: "POST",
        data: {email:email, pin:pin},
        type: 'json',
        success: function(r) {
            if(r.success) {
                window.location.reload();
            }
            else {
                window.alert("Login credentials incorrect, please try again");
            }
            button.removeClass('is-loading');
        },
        error: function(e) {
            console.log(e);
            window.alert("Unable to connect to server. Please try again later");
            button.removeClass('is-loading');
        }
    })
}

function check_enter(event) {
    if(event.keyCode === 13) {  // Checks if enter key is selected
        submit_login();
    }
}


/*
CHANGE PICKS PAGE
 */
function submit_change_picks() {
    return false;
}