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
    });
}

function check_enter(event) {
    if(event.keyCode === 13) {  // Checks if enter key is selected
        submit_login();
    }
}

/*
CHANGE PICKS PAGE
 */
function submit_change_picks(form) {
    let button = $("#submit-picks-button");
    button.addClass('is-loading');

    if (!check_entire_form(false)) {
        window.alert("Form requirements not met");
        return false;
    }
    $.post('submit-changes', form.serialize(), function (response) {
        window.alert(response);
    }).fail(function() {
        window.alert("Server Error: Please try again later");
    }).done(function() {
        button.removeClass('is-loading');
    });
    return false;
}

function revert_picks() {
    /* Revert main levels */
    $(".player-checkbox").each(function() {
        let checkbox = $(this);
        const pid = checkbox.val().split("*")[1];
        checkbox.prop('checked', initialMainLevels.includes(pid));  //Will check if included in picks

        // Manually need to call effects
        select_player(checkbox);
    });

    // Remove then add level 4
    $("#level-4-picks").find("tr").each(function() {
       remove_level_4($(this));
    });
    for(let i = 0; i < 2; i++) {add_level_4(initialLevel4Names[i], initialLevel4Ids[i]);}   // Revert Level 4s
}

$(document).ready(function() {
    try {
        revert_picks(); // Ensures form starts with current picks
    } catch (e) {}
});
