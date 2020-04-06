/* Element Caching */
let modal = $("#standings-modal");
let modalCardBody = modal.find(".modal-card-body");

function attach_prompt_modal() {    // Must be re-attached after refresh
    $(".pickset-row").find('td:not(.td-filter, .td-star)').click(function() {
        let row = $(this).closest("tr");
        prompt_pickset_modal(row.data("psid"), row.find(".td-name").text(), row.find(".td-pos").text());
    });
    $(".player-row").click(function() {
        let row = $(this);
        prompt_player_modal(row.data('pid'), row.find('.td-name').text(), row.find('.td-pos').text());
    });
}

function close_modal() {
    modal.removeClass("is-active");
    $("body").removeClass('modal-open');
}

// Closes Modal when esc is pressed
$(document).keyup(function(e) {
    if(e.keyCode === 27) close_modal();
});


/* Pickset Modal */
function prompt_pickset_modal(psid, name, pos) {
    /* Open Modal */
    modal.addClass("is-active modal-open");
    modalCardBody.html(ripple_html);

    /* Set modal header */
    modal.find(".modal-card-title").text(pos + " | " + name);

    /* Get modal body */
    $.get(window.location.href+"/get-pickset-modal", {psid:psid, channel_tid:channelTid}, function(response) {
        modalCardBody.html(response);
    }).fail(function() {
        window.alert("Server Error: Could not load info");
        close_modal();
    });
}

function organize_table(isChecked) {
    let tbody = $('#current-tournament-section').find('.table').find('tbody');
    if(isChecked)
        separate_picks_table(tbody);
    else
        combine_picks_table(tbody);
}

function separate_picks_table(tbody) {
    let rows = tbody.find(".pick-row").detach();
    let categories = {
        'Scoring Points': [],
        'Level 1': [],
        'Level 2': [],
        'Level 3': [],
        'Level 4': []
    };
    /* Separate by levels and scoring points */
    rows.each(function () {
        let row = $(this);
        const k = "Level " + row.data('level');
        categories[k].push(row);

        if(parseInt(row.find(".td-points").text()) > 0) // If player has any points
            categories["Scoring Points"].push(row.clone());
    });

    /* Add to DOM */
    for(const title in categories) {
        tbody.append("<tr><th class='has-text-centered' colspan='4'>" + title + "</th></tr>");
        tbody.append(categories[title]);
    }
}

function combine_picks_table(tbody) {
    let rows = $('.pick-row').detach();
    tbody.empty();
    let added = [];
    rows.each(function() {
        const row = $(this);
        const pid = row.data('pid');
        if(!added.includes(pid))
            tbody.append(row);
        added.push(pid);
    });
}

function pickset_switch_tabs(li_element) {
    let tabs = modal.find(".tabs");

    // Highlight Active Tab
    tabs.find("li").removeClass("is-active");
    li_element.addClass('is-active');

    if(li_element.data('index') === 0) {    // figure out which tab to open
        $("#current-tournament-section").show();
        $("#tournament-history-section").hide();
    }
    else {
        $("#tournament-history-section").show();
        $("#current-tournament-section").hide();
    }
}

/* Player Modal */
function prompt_player_modal(pid, name, pos) {
    /* Open Modal */
    modal.addClass("is-active modal-open");
    modalCardBody.html(ripple_html);

    /* Set modal header */
    modal.find(".modal-card-title").text(pos + " | " + name);

    /* Get modal body */
    $.get(window.location.href+"/get-player-modal", {pid:pid, channel_tid:channelTid}, function(response) {
        modalCardBody.html(response);
    }).fail(function() {
        window.alert("Server Error: Could not load info");
        close_modal();
    });
}