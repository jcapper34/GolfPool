let refreshButton = $("#refresh-standings").find("i");

function standings_refresh() {
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

        standings_cookie();
        attach_prompt_modal();
        attach_filter_checkbox();
        put_time_stamp();
    }).fail(function(e) {
            console.log(e);
            window.alert("Unable to refresh. Please try again later");
    }).always(function() {
       standingsTables.show();
       standingsLoaderBox.hide();
    });
}

// TODO:
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

function put_time_stamp() {
    let date = new Date();
    let period = 'am';
    if(date.getTime() > 12)
        period = 'pm';
    const hours = ("0" + (date.getHours() % 12)).slice(-2);
    const minutes = ("0" + date.getMinutes()).slice(-2);
    const seconds = ("0" + date.getSeconds()).slice(-2);
    $("#refresh-time").text([hours, minutes, seconds].join(":") + period);
}

$(document).ready(function() {
    standings_cookie();
    // window.setTimeout(standings_refresh, 1000*60);    // Refresh standings every 60 seconds
    put_time_stamp();
});