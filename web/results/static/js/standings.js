/*
ELEMENT CACHING
*/

let standingsMainSection = $("#standings-main-section");

/*
HTML Inserts
*/

function toggle_mobile_standings_menu(burger) {
    $('#standings-menu-items').stop().slideToggle();
    burger.toggleClass("menu-open");
}

let standings_xhr = null;
function switch_tournament(a_element) {
    toggle_mobile_standings_menu($("#standings-menu-header").find(".burger"));

    let menuLinks = $("#standings-menu-items").find("a");
    const newHref = a_element.data('href');
    if(a_element.hasClass('is-active'))  // Pages aren't changing
        return;

    if(standings_xhr !== null) // Abort current request
        standings_xhr.abort();

    window.history.pushState("", "", newHref);  //Change page url

    // Set open tab to active
    menuLinks.removeClass('is-active');
    a_element.addClass('is-active');

    standingsMainSection.html(roller_html); // Put loader

    // Get standings section by ajax
    standings_xhr = $.get(newHref, {main_section_only: true}, function(response) {
        standingsMainSection.html(response);

        // Re-attach handlers
        attach_prompt_modal();
        attach_filter_checkbox();
        putTimeStamp();
    });
}

/*
Standings Header
*/
function tournament_search() {
    const val = $("#tournament-search").val().toLowerCase().trim();
    const size = val.length;
    $(".td-name").each(function(){
        const name = $(this).text().toLowerCase();
        if((name.substring(0, size) === val) || (name.split(" ")[1].substring(0, size) === val)) {
            $(this).closest("tr").show();
        }
        else {
            $(this).closest("tr").hide();
        }
    });
}

/*
Standings Tables
*/
function attach_filter_checkbox() {    // Must be re-attached after refresh
    const filter_checkbox = function(e, picks) {
        if (e.prop("checked") === true) {
            $(".player-row").each(function () {
                let row = $(this);
                let found = false;
                $.each(picks, function (index, pid) {
                    if (row.data('pid') == pid)
                        found = true;
                });
                if (found)
                    row.show();
                else
                    row.hide();
            });
        }
    };

    $(".filter-checkbox").change(function () {
        let e = $(this);
        let row = e.closest(".pickset-row");

        if (e.prop("checked")) {
            $(".filter-checkbox:checked").each(function () {
                if (!$(this).is(e)) {
                    $(this).prop("checked", false);
                }
            });

            // Checks if already has picks stored
            const data_picks = row.data("picks");
            if (data_picks !== undefined && data_picks.length > 0) {
                filter_checkbox(e, data_picks);
            }
            else {
                const path = window.location.pathname + "/get-pickset";
                const psid = row.data("psid");
                $.ajax({
                    url: path,
                    data: {"psid": psid},
                    dataType: "json",
                    success: function (picks) {
                        filter_checkbox(e, picks);
                    },
                    error: function (e) {
                        console.log(e);
                        window.alert("Unable to connect to server");
                    }
                });
            }
        }
        else {
            $(".player-row").show();
        }
    });
}

function switch_table(e) {
    $("#leaderboard-table-column").toggle();
    $("#standings-table-column").toggle();

}

function generateSpreadsheet() {
    window.location.replace(window.location.href + "/generate-xl");
}

/*
On startup
*/
$(document).ready(function() {
    $(".filter-checkbox").prop("checked", false);   //Uncheck all player filters

    tournament_search();
    attach_prompt_modal();
    attach_filter_checkbox();

});