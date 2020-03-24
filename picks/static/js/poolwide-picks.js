/*
Parameters:
- year
 */

function prompt_picks_table(li_element) {
    // Highlight selected tab
    $('#picks-tabs').find('li').removeClass('is-active');
    li_element.addClass('is-active');

    $("#most-picked-section").addClass('hide');
    $("#all-picks-section").removeClass('hide');
}

var mostPickedLoaded = false;
function prompt_most_picked(li_element) {
    animate_progress();

    // Highlight selected tab
    $('#picks-tabs').find('li').removeClass('is-active');
    li_element.addClass('is-active');

    let mostPickedSection = $("#most-picked-section");
    mostPickedSection.removeClass('hide');
    $("#all-picks-section").addClass('hide');

    if(!mostPickedLoaded) { // If not yet loaded
        $.get('/picks/most-picked/'+year, function(htmlResponse) {
            mostPickedSection.html(htmlResponse);
            animate_progress();
        });
    }
}

function organize_most_picked() {
    let mostPickedTableBody = $("#most-picked-section").find("tbody");

    if($("#organize-most-picked").prop("checked")) {
        // Separate rows into an array
        let level_players = [[],[],[],[]];
        $(".most-picked-row").each(function() {
            const row = $(this).detach();
            level_players[row.data("level")-1].push(row);
        });
        for(let i = 0; i < 4; i++) {
            mostPickedTableBody.append("<tr><th colspan='3' class='has-text-centered'>Level " + String(i+1) + "</th></tr>")
                .append(level_players[i]);
        }
    } else {
        let rows = [];
        $(".most-picked-row").each(function() {
            const row = $(this);
            if(!rows.includes(row))
                rows.push(row);
        });
        rows.sort(function(a, b) {  // Sort by num picked
            return parseInt($(b).find(".num-picked").text()) - parseInt($(a).find(".num-picked").text());
        });
        mostPickedTableBody.empty().append(rows);
    }
    animate_progress();
}


function animate_progress() {
    let row = $(".most-picked-row");
    const max = parseInt(row.find("progress").eq(0).data("end"));

    row.each(function () {
        let progress_bar = $(this).find("progress");
        const end = parseInt(progress_bar.data("end"));
        let val_label = $(this).find(".num-picked");
        $({val: 0}).animate({val: end}, {
            duration: 1000,
            step: function (now) {
                progress_bar.val((now / max) * 100);
                val_label.text(Math.ceil(now));
            }
        });
    });
}

