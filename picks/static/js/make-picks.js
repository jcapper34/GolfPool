/*
ELEMENT CACHING
*/
let generalInputs = $(".general-input");
let playerCheckboxes = $(".player-checkbox");

/*
ENTIRE FORM
 */

// Checks form on submission
function submit_make_picks() {
    if(check_entire_form(true)) {
        //Check for inconsistent name-pid pairs
        $(".level-4-hidden").each(function () {
            if($(this).val() === '') {
                $(this).val("None");
            }
        });

        let confirmMessage = "Are you sure you would like to submit? You can change your picks later by using your PIN\n\n";
        confirmMessage += "Your Picks are:\n\n";
        for(let level = 1; level <= 4; level++) {
            confirmMessage += 'Level ' + level + '\n';
            let selector = "input[name='level-" + level + "']";
            if(level !== 4)
                selector += ":checked";
            $(selector).each(function () {
                confirmMessage += $(this).val().split('*')[0] + '\n';
            });
            confirmMessage += '\n';
        }
        return window.confirm(confirmMessage);

    }
    window.alert("Please complete entire form and/or fix errors before submitting");
    return false;
}

function check_entire_form(checkGeneral) {
    let valid = true;

    if(checkGeneral) {
        // Checking general fields
        for (let i = 0; i < generalInputs.length; i++) {
            const success = general_field_checker(generalInputs.eq(i));
            if (success === undefined || !success)
                return false;
        }
    }

    const mainLevelBoxes = $(".main-level-box");
    for(let i = 0; i < mainLevelBoxes.length; i++){
        if(!check_main_level(mainLevelBoxes.eq(i)))
            return false;
    }

    // Checking level 4
    if(!check_all_level_4())
        return false;

    return valid;
}

/*
GENERAL FIELDS
 */

function general_field_checker(elementSelector) {
    const fieldName = elementSelector.attr("name");

    let check_func;
    if(fieldName === 'name')
        check_func = check_name_input;
    else if(fieldName === 'email')
        check_func = check_email_input;
    else if(fieldName === 'pin')
        check_func = check_pin_input;

    const success = check_func(elementSelector);
    if(success !== undefined) {
        do_general_effects(success, elementSelector);
    }
    return success;
}

$(".general-input[name='name']").keyup(function() {
    let e = $(this);
    const val = e.val();
    if(val === '')
        return;

    let words = val.split(" ");
    for(let i = 0; i < words.length; i++) {
        if(words[i].length > 0)
            words[i] = words[i][0].toUpperCase() + words[i].substring(1);
    }
    e.val(words.join(" "));
});

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

playerCheckboxes.change(function() {
    select_player($(this));
});

function select_player(checkbox) {
    let pickBox = checkbox.closest(".pick-box");
    check_main_level(pickBox, checkbox);
    main_level_effects(pickBox);
}

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

    playerDetailsBox.find("img").each(function() {
        $(this).attr('src', $(this).data('src'));   // Load Image
    });
    if(checkBox.prop('checked'))  //Show Details
        playerDetailsBox.stop().slideDown();
    else  //Hide Details
        playerDetailsBox.stop().slideUp();
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

function player_checkbox_color_effect() {
    let label = $(".player-checkbox").parent().find('.button');
    const finalR = 125;
    const finalG = 125;
    const finalB = 125;

    $({percent: 1.0}).animate({percent: 0}, {
        duration: 1000,
        step: function(now, fx) {
            const r = Math.round(now*finalR);
            const g = Math.round(now*finalG);
            const b = Math.round(now*finalB);
            label.css("background-color", "rgb(" + r + ',' + b + ',' + g + ")");
        }
    });
}

/*
LEVEL 4 Functions
*/

function create_player_suggestions(input_element) {
    const numSuggestions = 5;
    const val = input_element.val().toLowerCase();
    if(val === '') {// If no value, then don't do anything
        $("#suggestions-box").addClass('hide');
        return;
    }

    const isValid = function(pid) {
        let valid = true;

        $("input[name='level-4']").each(function() {    // Check if already picked
            if($(this).val().split('*')[1] === pid)
                valid = false;
        });

        $(".player-column").each(function() {   // Check if in levels 1-3
            // out($(this).data('pid'));
            if(String($(this).data('pid')) === pid)
                valid = false;
        });
        return valid;
    };
    const nameCheck = function(name, val) {
        return name.substr(0, val.length).toLowerCase() === val;
    };

    let suggestions = [];
    let count = 0;
    for(const i in apiPlayers) {
        const player = apiPlayers[i];

        const playerFirst = player.name.split(' ')[0];
        const playerLast = player.name.split(' ')[1];

        if ( (nameCheck(playerFirst, val) || nameCheck(playerLast, val) || nameCheck(player.name, val)) && isValid(player.id)){
            suggestions.push([player.id, player.name]); // In the form (pid, name)
            count++;
            if (count === numSuggestions)
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

function add_level_4(name, pid) {

    /* Reset inputs */
    $("#suggestions-box").addClass('hide');

    let textInput = $("#level-4-text");
    textInput.val('');

    let picksTable = $("#level-4-picks");
    const numPicked = picksTable.find("tr").length;
    if(numPicked < 2 ) {
        if(numPicked === 1)
            textInput.prop('disabled', true);
        picksTable.append("<tr>" +
            "<td>" + name + "</td>" +
            "<td><a onclick='remove_level_4($(this).closest(\"tr\"))'><i class='fa fa-times'></i></td>" +
            "<td class='hide'><input type='hidden' name='level-4' value='" + [name, pid].join('*') + "'></td>" +
            "</tr>"
        );  //If changing, make sure to change macro as well
    }
}

function remove_level_4(trElement) {
    trElement.remove();
    $("#level-4-text").removeAttr('disabled');

}

function check_all_level_4() {
    const level4Inputs = $("input[name='level-4']");
    if(level4Inputs.length !== 2 || level4Inputs.eq(0).val() === level4Inputs.eq(1).val())   // Check if correct number and the picks don't match
        return false;

    let valid = true;
    level4Inputs.each(function () {
        if($(this).val() === '')
            valid = false;
    });
    return valid;
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

/*
PAGE STARTUP
*/

// OWGR RANKINGS. ONLY USED TO SET RANKINGS OF LEVELS
let OWGR_rankings;
function set_OWGR() {
    $.post('/api-retriever', {url: OWGR_URL}, function (response) {
        OWGR_rankings = response;
        for(const i in OWGR_rankings) {  // Update player details
                const player = OWGR_rankings[i];
                let playerColumn = $(".player-column[data-pid='" + player.golferId + "']");
                playerColumn.find('.owgr-rank').text(player.currentRank);   // Show OWGR Rank
            }
        }
    );
}


var apiPlayers = {};
function get_api_players() {
    $.post('/api-retriever', {url: API_PLAYERS_URL}, function (response) {
        apiPlayers = Object.values(response.items);
        apiPlayers = append_to_api_players(apiPlayers);
        filter_api_players();

    }).fail(function (e) {
        window.alert("Unable to retrieve player data from server. Please try again later");
        out(e);
    });

}

function filter_api_players() {
    let filteredPlayers = [];
    for(const i in apiPlayers) {
        if(apiPlayers[i].type === 'golfer')
            filteredPlayers.push(apiPlayers[i]);
    }
    apiPlayers = filteredPlayers;
}

function append_to_api_players(api_list) {  //Allows me to add popular players that don't show up
    const newPlayers = [
        // {
        //     id: 43344,
        //     name: "Si Woo Kim",
        //     firstName: 'Si Woo',
        //     lastName: 'Kim',
        //     type: 'golfer'
        // },
        {
            id: 74401,
            name: "Erik van Rooyen",
            firstName: 'Erik',
            lastName: 'van Rooyen',
            type: 'golfer'
        },
        {
            id: 37873,
            name: "CT Pan",
            firstName: 'Cheng Tsung',
            lastName: 'Pan',
            type: 'golfer'
        },
        // {
        //     id: 56542,
        //     name: "Christiaan Bezuidenhout",
        //     firstName: 'Christiaan',
        //     lastName: 'Bezuidenhout',
        //     type: 'golfer'
        // },
        // {
        //     id: 37455,
        //     name: "Dylan Frittelli",
        //     firstName: 'Dylan',
        //     lastName: 'Frittelli',
        //     type: 'golfer'
        // },

    ];
    return api_list.concat(newPlayers);
}

function set_season_history() {
    $.get('/picks/season-history', function(response) {
        $(".pool-ranking-column").attr("rowspan", response.length); //Set height of table

        $(".player-column").each(function() {
            const pid = $(this).data('pid');
            let posColumn = $(this).find('.pos-history');
            for(let i = 0; i < response.length; i++) {  // Get ranking from each year
                const year_history = response[i];
                const year = year_history[0];
                let pos = '-';
                if(year_history[1].hasOwnProperty(pid))
                    pos = year_history[1][pid];

                if(i === 0)
                    posColumn.text([year, pos].join(": "));
                else
                    posColumn.closest('table').append("<tr><td>" + [year, pos].join(": ") + "</td></tr>")
            }

        });
    });
}


/*
MAIN FUNCTION
 */
$(document).ready(function() {
    // Do effects for starting state
    $(".main-level-box").each(function() {
       main_level_effects($(this));
    });
    $(".show-details:checked").each(function() {main_level_player_details($(this))});

    // Retrieve API Data
    set_OWGR();
    get_api_players();
    set_season_history();
});
