/* HTML Inserts */
const ripple_html = "<div class='lds-ripple'><div></div><div></div></div>";


/* Modals */
function close_modal() {
    $("#tournament-modal").fadeOut(function() {
        $(this).removeClass("is-active");
    });
    $("body").removeClass('modal-open');
}

function prompt_pickset_modal(psid, name, pos) {
    let modal = $("#standings-modal").addClass("is-active");

    /* Set modal header */


    // TODO: Modal Loader


    /* Get modal body */
    $.get(window.location.href+"/get-pickset-modal", {psid:psid}, function(response) {
        modal.find(".modal-card-body").html(response);
    });
}

function attach_prompt_modal() {
    $(".pickset-row").find('td:not(.td-filter, .td-star)').click(function() {
        let row = $(this).closest("tr");
        prompt_pickset_modal(row.data("psid"), row.find(".td-name").text(), row.find(".td-pos").text());
    });
}

function toggle_slider(e) {
    let icon = e.find(".icon i");
    e.next().closest(".collapse-wrapper").stop().slideToggle(function() {
        icon.toggleClass("fa-angle-down");
        icon.toggleClass("fa-angle-up");
    });
}

// Closes Modal when esc is pressed
$(document).keyup(function(e) {
    if(e.keyCode === 27) close_modal();
});


/* Standings Header */
function standings_search() {
    const val = $("#tournament-search").val().toLowerCase();
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
$("#tournament-search").keyup(standings_search);

function standings_refresh() {
    let button = $(this).find("i");
    // Rotate link
    $({deg: 0}).animate({deg: 360}, {
        duration: 1000,
        step: function(now) {
            button.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });

    // Retrieve Standings
    let standings_tables = $("#tournament-tables").html(ripple_html);
    $.ajax({
        url: window.location.pathname,
        data: {refresh: true, tid: tid},
        success: function(r) {
            standings_tables.html(r);

            standings_cookie();
            attach_prompt_modal();
            attach_filter_checkbox();
            switch_table($("#table-switch"));
        },
        error: function(e) {
            console.log(e);
            window.alert("Unable to refresh. Please try again later");
        }
    })
}
$("#refresh-tournament").click(standings_refresh);

/* Standings Tables */
function switch_table(e) {
    let label = e.parent().find("label");
    if(!e.prop('checked')) {
        label.text("Leaderboard");
        $("#leaderboard-table-column").show();
        $("#tournament-table-column").hide();
    }
    else {
        label.text("Standings");
        $("#leaderboard-table-column").hide();
        $("#tournament-table-column").show();
    }

}

function attach_filter_checkbox() {
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

/* Cookies */
function standings_cookie() {
    if((is_live) && (navigator.cookieEnabled)) {
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
$(document).ready(function(){
    $(".filter-checkbox").prop("checked", false);
    // standings_search();
    // standings_cookie();
    attach_prompt_modal();
    attach_filter_checkbox();
});