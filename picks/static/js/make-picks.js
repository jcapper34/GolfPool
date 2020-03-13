/*
FORM VALIDATING
 */
function check_general_input(e) {
    const name = e.attr('name');
    const val = e.val();
    let field = e.closest(".field");

    // No flags if no value
    if(val === '') {
        e.removeClass("is-success").removeClass("is-danger");
        field.find(".fa-check, .fa-exclamation-triangle").addClass('hide');
        return;
    }

    let valid = false;

    if(name === 'name') {               // For Name
        valid = ( (isNaN(val)) && (val.length > 2) );
    }
    else if(name === 'email') {         // For Email
        valid = ( (val.length > 3) && (val.includes("@")) && (val.includes(".")) && (val.indexOf("@") > 0));
    }
    else if(name === 'pin') {           // For PIN
        valid = ( (!isNaN(val)) && (val.length === 4) );
    }


    if (valid) {
        e.addClass("is-success").removeClass("is-danger");
        field.find(".fa-check").removeClass('hide');
        field.find(".fa-exclamation-triangle").addClass('hide');
    }
    else {
        e.addClass("is-danger").removeClass("is-success");
        field.find(".fa-exclamation-triangle").removeClass('hide');
        field.find(".fa-check").addClass('hide');
        field.addClass('tooltip is-tooltip-active');
        window.setTimeout(function() {
            field.removeClass('tooltip is-tooltip-active');
        }, 1500);
    }

    return valid;
}

function check_all_general() {
    let valid = true;
    $(".general-input").each(function () {
        if (!check_general_input($(this))) {
            valid = false;
        }
    });

    let check_icon = $('#make-picks-menu').find(".check-icon").eq(0);
    if(valid)
        check_icon.removeClass('hide');
    else
        check_icon.addClass('hide');

    return valid;
}

function check_main_level(pickBox, recently_selected) {
    const picksAllowed = pickBox.data('allowed');
    let len = pickBox.find(".player-checkbox:checked").length;
    const level = pickBox.data('level');
    let check_icon = $('#make-picks-menu').find('.check-icon').eq(level);

    if ((len > picksAllowed) && (recently_selected !== undefined)) {
        recently_selected.prop("checked", false);
        len--;
    }
    if (len === picksAllowed) {
        check_icon.removeClass('hide');
        return true;
    }
    else {
        check_icon.addClass('hide');
        return false;
    }
}

$(".player-checkbox").change(function() {
    let pick_box = $(this).closest(".pick-box");
    if(pick_box.find(".player-checkbox:checked").length > 0) {
        pick_box.find(".reset-level").fadeIn()
    }
    else {
        pick_box.find(".reset-level").fadeOut()
    }

    check_main_level($(this).closest('.pick-box'), $(this));
    set_progress();
});

function check_entire_form() {
    let valid = true;

    // Check general fields
    if( !check_all_general() )
        valid = false;

    // Check all main level picks
    $(".pick-box").each(function() {
        const level = $(this).data('level');
        if((level > 0) && (level < 4))
            if( !check_main_level($(this)) )
                valid = false;
    });

    if( !check_level_4() )
        valid = false;

    return valid;

}

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