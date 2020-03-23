function prompt_pickset_modal(psid, name, pos) {
    let modal = $("#standings-modal").addClass("is-active modal-open");

    /* Set modal header */
    modal.find(".modal-card-title").text(pos + " | " + name);
    // TODO: Modal Loader


    /* Get modal body */
    $.get(window.location.href+"/get-pickset-modal", {psid:psid}, function(response) {
        modal.find(".modal-card-body").html(response);
    }).fail(function() {
        window.alert("Server Error: Could not load info");
    });
}

function attach_prompt_modal() {
    $(".pickset-row").find('td:not(.td-filter, .td-star)').click(function() {
        let row = $(this).closest("tr");
        prompt_pickset_modal(row.data("psid"), row.find(".td-name").text(), row.find(".td-pos").text());
    });
}

function organize_table(isChecked) {
    let table = $('#current-tournament-section').find('.table');
    if(isChecked)
        separate_picks_table(table);
    else
        combine_picks_table(table);
}

function separate_picks_table(table) {
    let rows = table.find(".pick-row").detach();
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
        table.append("<tr><th class='has-text-centered' colspan='4'>" + title + "</th></tr>");
        table.append(categories[title]);
    }
}

function combine_picks_table(table) {
    let rows = $('.pick-row').detach();
    table.empty();
    let added = [];
    rows.each(function() {
        const row = $(this);
        const pid = row.data('pid');
        if(!added.includes(pid))
            table.append(row);
        added.push(pid);
    });
}

function close_modal() {
    $("#standings-modal").removeClass("is-active");
    $("body").removeClass('modal-open');
}

// Closes Modal when esc is pressed
$(document).keyup(function(e) {
    if(e.keyCode === 27) close_modal();
});

