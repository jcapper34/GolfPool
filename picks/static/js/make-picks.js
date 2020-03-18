/*
ENTIRE FORM
 */

// Checks form on submission
$("#make-picks-form").submit(function() {
    if(check_entire_form()) {
        //Check for inconsistent name-pid pairs
        $(".level-4-hidden").each(function () {
            if($(this).val() === '') {
                $(this).val("None");
            }
        });

        return window.confirm("Are you sure you would like to submit? You can change your picks later by using your PIN");

    }

    window.alert("Please complete entire form and/or fix errors before submitting");
    return false;
});

function check_entire_form() {
    let valid = true;

    // Checking general fields
    $('.general-input').each(function() {
        const success = general_field_checker($(this));
        if(success === undefined || !success)
            valid = false;
    });

    return valid;
}

/*
GENERAL FIELDS
 */

function general_field_checker(elementSelector) {
    const fieldName = elementSelector.attr("name");

    let check_func;
    if(fieldName === 'name') check_func = check_name_input;
    else if(fieldName === 'email') check_func = check_email_input;
    else if(fieldName === 'pin') check_func = check_pin_input;

    const success = check_func(elementSelector);
    if(success !== undefined) {
        do_general_effects(success, elementSelector);
    }
    return success;
}

function check_name_input(elementSelector) {
    const val = elementSelector.val();
    if(val === '') {
        return clear_general_flags(elementSelector);
    }

    return (isNaN(val)) && (val.length > 2);
}

function check_email_input(elementSelector) {
    const val = elementSelector.val();
    if(val === '') {
        return clear_general_flags(elementSelector);
    }
    return (val.length > 3) && (val.includes("@")) && (val.includes(".")) && (val.indexOf("@") > 0);
}

function check_pin_input(elementSelector) {
    const val = elementSelector.val();
    if(val === '') {
        return clear_general_flags(elementSelector);
    }
    return (!isNaN(val)) && (val.length === 4);
}

function do_general_effects(success, elementSelector) {
    let field = elementSelector.closest(".field");
    if (success) {
        elementSelector.addClass("is-success").removeClass("is-danger");
        field.find(".fa-check").removeClass('hide');
        field.find(".fa-exclamation-triangle").addClass('hide');
    }
    else {
        elementSelector.addClass("is-danger").removeClass("is-success");
        field.find(".fa-exclamation-triangle").removeClass('hide');
        field.find(".fa-check").addClass('hide');
        field.addClass('tooltip is-tooltip-active');
        window.setTimeout(function() {
            field.removeClass('tooltip is-tooltip-active');
        }, 1500);
    }
}

function clear_general_flags(elementSelector) {
    let field = elementSelector.closest('.field');
    elementSelector.removeClass("is-success").removeClass("is-danger");
    field.find(".fa-check, .fa-exclamation-triangle").addClass('hide');
}

/*
MAIN LEVEL FIELDS
 */

$(".player-checkbox").change(function() {
    let pickBox = $(this).closest(".pick-box");
    check_main_level(pickBox, $(this));
    main_level_effects(pickBox);
});

function check_main_level(pickBox, recently_selected) {
    const picksAllowed = pickBox.data('allowed');
    let len = pickBox.find(".player-checkbox:checked").length;
    const level = pickBox.data('level');

    if ((len > picksAllowed) && (recently_selected !== undefined)) {
        recently_selected.prop("checked", false);
        len--;
    }
    return len === picksAllowed;
}

function main_level_player_details(checkBox) {
    let pickBox = checkBox.closest('.pick-box');
    let playerDetailsBox = pickBox.find(".player-details");
    if(checkBox.prop('checked')) {  //Show Details
        playerDetailsBox.slideDown();
        playerDetailsBox.find("img").each(function() {  //Load images
            $(this).attr("src", $(this).data('src'));
        });
    }
    else {  //Hide Details
        playerDetailsBox.slideUp();
    }
}

function main_level_effects(pickBox) {
    const numPicked = pickBox.find(".player-checkbox:checked").length;
    if(numPicked > 0) {   // If any players have been selected
        pickBox.find(".reset-level").fadeIn();
    }
    else {
        pickBox.find(".reset-level").fadeOut();
    }

    pickBox.find(".num-picked").text(numPicked);    // Update to show how many of that level were picked
}

function reset_main_level(pickBox) {
    pickBox.find('.player-checkbox').prop('checked', false);
    main_level_effects(pickBox);
}


/*
LEVEL 4 Functions
*/
function create_player_suggestions(input_element) {
    const val = input_element.val().toLowerCase();
    if(val === '') {// If no value, then don't do anything
        input_element.closest('.level-4-field').find('.suggestions-box').addClass('hide');
        return;
    }


    const nameCheck = function(name, val) {
        return name.substr(0, val.length).toLowerCase() === val;
    };

    let suggestions = [];
    let count = 0;

    for(let i = 0; i < OWGR_rankings.length; i++) {
        const player = OWGR_rankings[i];
        const playerFirst = player.plrName.first;
        const playerLast = player.plrName.last;
        const playerFull = [playerFirst, playerLast].join(' ');

        if (nameCheck(playerFirst, val) || nameCheck(playerLast, val) || nameCheck(playerFull, val)) {
            suggestions.push([player.plrNum, playerFull]); // In the form (pid, name)
            count++;
            if (count === 5)
                break;
        }
    }
    show_player_suggestions(input_element.closest('.level-4-field'), suggestions);

}


function show_player_suggestions(fieldElement, suggestions) {
    let suggestionsBox = $("#suggestions-box");
    suggestionsBox.removeClass("hide"); // Show Suggestions

    let i = 0;
    suggestionsBox.find(".level-4-option").each(function() {
        let td = $(this);
        if(i < suggestions.length) {
            /* Set and show option */
            td.removeClass("hide").
                find(".level-4-option-name")
                    .text(suggestions[i][1])
                    .data("pid", suggestions[i][0]);
        }
        else {
            /* Reset and hide option */
            td.addClass("hide").
                find(".level-4-option-name")
                    .empty()
                    .data("pid", "");
        }
        i++;
    });
}

function add_level_4(tdElement) {
    const name = tdElement.text();
    const pid = tdElement.data('pid');

    $("#suggestions-box").addClass('hide');


}

/*
EXTRA EFFECTS
*/

function shuffle_pin(button) {
    let input = button.closest('.field').find('.general-input');
    let newVal = String();
    for(let i = 0; i < 4; i++) {
        newVal += String(Math.floor((Math.random() * 10)));
    }
    input.val(newVal);
}

function toggle_show_pin(button) {
    let input = button.closest('.field').find('.general-input');
    if(input.attr('type') === 'password') {
        input.attr('type', 'text');
    }
    else {
        input.attr('type', 'password');
    }
}

/* PAGE STARTUP */
var OWGR_rankings;
$(document).ready(function() {
    // Insert OWGR
    $.ajax({
        url: OWGR_URL,
        type: 'GET',
        success: function (response) {
            OWGR_rankings = response.tours[0].years[0].stats[0].details;
            for(const i in OWGR_rankings) {  // Update player details
                const player = OWGR_rankings[i];
                $(".player-column[data-pid='" + player.plrNum + "']").find('.owgr-rank').text(player.curRank);
            }
        }
    });
});