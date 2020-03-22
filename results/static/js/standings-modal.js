function close_modal() {
    $("#standings-modal").fadeOut(function() {
        $(this).removeClass("is-active");
    });
    $("body").removeClass('modal-open');
}

function prompt_pickset_modal(psid, name, pos) {
    let modal = $("#standings-modal").addClass("is-active");

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