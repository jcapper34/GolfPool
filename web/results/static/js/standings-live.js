function standingsRefresh() {
    let refreshButton = $("#refresh-standings").find("i");
    let standingsTables = $("#standings-tables");
    let standingsLoaderBox = $("#standings-loader-box");
    let leaderboardTableColumn = $("#leaderboard-table-column");
    let standingsTableColumn = $("#standings-table-column");


    standingsLoaderBox.show();  // Show loader
    standingsTables.hide();

    // Spin link
    $({deg: 0}).animate({deg: 360}, {
        duration: 1000,
        step: function(now) {
            refreshButton.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });

    // Get new standings from Server
    $.get(window.location.pathname,{refresh: true},function(r) {
        standingsTableColumn.html(r[0]);   // Put standings table
        leaderboardTableColumn.html(r[1]);   // Put leaderboard table

        standingsTrendCookie();
        attach_prompt_modal();
        attach_filter_checkbox();
        putTimeStamp();
    }).fail(function(e) {
            console.log(e);
            window.alert("Unable to refresh. Please try again later");
    }).always(function() {
       standingsTables.show();
       standingsLoaderBox.hide();
    });
}


function putTimeStamp() {
    let date = new Date();
    let period = 'am';
    if(date.getHours() > 12)
        period = 'pm';
    const hours = ("0" + (date.getHours() % 12)).slice(-2);
    const minutes = ("0" + date.getMinutes()).slice(-2);
    const seconds = ("0" + date.getSeconds()).slice(-2);
    $("#refresh-time").text([hours, minutes, seconds].join(":") + period);
}


/* Standings Cookies */

function handle_pickset_favoriting(starA) {
    const psid = starA.closest(".pickset-row").data("psid");

    let icon = starA.find("i");
    icon.toggleClass("favorited");
    if(icon.hasClass("favorited")) {
        add_favorite_pickset(psid)
    } else {
        remove_favorite_pickset(psid);
    }
}

const FAVORITE_PLAYERS_COOKIE = "favorite-picksets";
function add_favorite_pickset(psid) {

    if(navigator.cookieEnabled) {
        const FAVORITE_PLAYERS_COOKIE = "favorite-players";
        let favoritesBefore = Cookies.getJSON(FAVORITE_PLAYERS_COOKIE);
        if(favoritesBefore === undefined)
            favoritesBefore = [];   // Initialize to empty list

        favoritesBefore.push(psid);
        Cookies.set(FAVORITE_PLAYERS_COOKIE, [], {
            expires: 90,    // 90 days
            SameSite: 'lax'
        });
    }
}

function remove_favorite_pickset(psid) {
    out(psid);
    // if(navigator.cookieEnabled) {
    //     const FAVORITE_PLAYERS_COOKIE = "favorite-players";
    //     let favoritesBefore = Cookies.getJSON(FAVORITE_PLAYERS_COOKIE);
    // }
}

function show_favorite_picksets() {
    if(navigator.cookieEnabled) {
        let standingsTable = $("#standings-table");
        /* Show favorite icons */
        standingsTable.find(".th-star").removeClass('hide'); //Extra space to table heading
        $(".pickset-row").each(function () {
            $(this).append("<td>" +
                            "<a class='icon' onclick='handle_pickset_favoriting($(this))'>" +
                            "<i class='fas fa-star favorite-star'></i>" +
                            "</a>" +
                            "</td>");
        });

        /* Display favorites section */
        const favorites = Cookies.getJSON(FAVORITE_PLAYERS_COOKIE);
        if (favorites === undefined)
            return;
    }
}

const STANDINGS_TREND_COOKIE = "last-tournament";
function standingsTrendCookie() {
    if(navigator.cookieEnabled) {
        let pickset_rows = $(".pickset-row");
        let old_standings = Cookies.getJSON(STANDINGS_TREND_COOKIE);
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
        Cookies.set(STANDINGS_TREND_COOKIE, standings, {
            expires: 2,
            SameSite: 'lax'
        });
    }
}

$(document).ready(function() {
    standingsTrendCookie();
//    show_favorite_picksets();
    // window.setTimeout(standings_refresh, 1000*60);    // Refresh standings every 60 seconds
    putTimeStamp();
});
