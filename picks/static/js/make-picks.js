/*
ENTIRE FORM
 */

// Checks form on submission
$("#make-picks-form").submit(function() {
    const form_validated = check_entire_form();
    if(form_validated) {
        //Check for inconsistent name-pid pairs
        $(".level-4-hidden").each(function () {
            if($(this).val() === '') {
                $(this).val("None");
            }
        });

        const confirmed = window.confirm("Are you sure you would like to submit? You can change your picks later by using your PIN");
        if(confirmed) {
            return true;
        }
    }
    else {
        window.alert("Please complete entire form and/or fix errors before submitting");
    }

    return false;
});

function check_entire_form() {
    let valid = true;

    // Checking general fields
    $('.general-input').each(function() {
        const success = !general_field_checker($(this));
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
