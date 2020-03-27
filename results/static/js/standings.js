/* ELEMENT CACHING */
let tournamentSearchInput = $("#tournament-search");
let leaderboardTableColumn = $("#leaderboard-table-column");
let standingsTableColumn = $("#standings-table-column");

/* HTML Inserts */
const ripple_html = "<div class='lds-ripple'><div></div><div></div></div>";


/* Mobile Menu */
function toggle_mobile_menu() {

}


/* Standings Header */
function tournament_search() {
    const val = tournamentSearchInput.val().toLowerCase().trim();
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

/* Standings Tables */
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
    leaderboardTableColumn.toggle();
    standingsTableColumn.toggle();

}


/* Live Standings */
function standings_refresh() {
    // Spin link
    let button = $("#refresh-standings").find("i");
    $({deg: 0}).animate({deg: 360}, {
        duration: 1000,
        step: function(now) {
            button.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });

    // Retrieve Standings
    let standings_table = standingsTableColumn.html(ripple_html);
    let leaderboard_table = leaderboardTableColumn.html(ripple_html);

    // Get new standings from Server
    $.get(window.location.pathname,{refresh: true},function(r) {
        standings_table.html(r[0]);   // Put standings table
        leaderboard_table.html(r[1]);   // Put leaderboard table

        // standings_cookie();
        attach_prompt_modal();
        attach_filter_checkbox();
        // switch_table($("#table-switch"));
    }).fail(function(e) {
            console.log(e);
            window.alert("Unable to refresh. Please try again later");
        });
}

// TODO: Live Standings Cookies
function standings_cookie() {
    if(navigator.cookieEnabled) {
        const cookie_name = "last-tournament";
        let pickset_rows = $(".pickset-row");
        let old_standings = Cookies.getJSON(cookie_name);
        if(old_standings !== undefined) {
            pickset_rows.each(function() {
                let td_pos = $(this).find(".td-pos");
                const old_pos = old_standings[$(this).data("psid")];
                const current_pos = parseInt(td_pos.text());
                if(current_pos > old_pos) {
                    td_pos.html("<i class='fas fa-arrow-down' style='font-size:8px'></i>" + current_pos);
                }
                else if(current_pos < old_pos) {
                    td_pos.html("<i class='fas fa-arrow-up' style='font-size:8px'></i>" + current_pos);
                }
                else {
                    td_pos.html("&nbsp;" + current_pos);
                }
            });
        }

        let standings = {};
        pickset_rows.each(function() {
            standings[$(this).data("psid")] = parseInt($(this).find(".td-pos").text());
        });
        Cookies.set(cookie_name, standings, { expires: 2 });
    }
}


/* On startup */
$(document).ready(function() {
    $(".filter-checkbox").prop("checked", false);   //Uncheck all player filters

    tournament_search();
    // standings_cookie();
    attach_prompt_modal();
    attach_filter_checkbox();
});