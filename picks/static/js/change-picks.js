$.ajaxSetup({ traditional: true });

function set_to_default() {
    $(".select").removeClass("is-danger");
    $(".pick-select").each(function() {
        $(this).find("option[data-original='original']").prop("selected", true);
    });
}

$(".pick-select").change(function () {
    let e = $(this);
    const val = e.val();

    let duplicates = [];
    $(this).closest('.pick-column').find(".pick-select").each(function() {
        if ($(this).val() === val) {
            duplicates.push($(this).parent());
        }
    });
    if(duplicates.length > 1) {
        for(let i = 0; i < duplicates.length; i++) {
            duplicates[i].addClass("is-danger");
        }
    }
    else {
        $(".select").removeClass("is-danger");
    }
});

$("#save-changes").click(function() {
    let button = $(this);
    let valid = true;
    const container = $("#change-picks-container");
    let data = {
        "psid": container.data("psid"),
        "psname": container.data("psname"),
        "email": container.data("email")
    };
    for(let i = 1; i <= 4; i++) {
        let pick_level = [];
        $(".level-"+i+"-input").each(function () {
            if(($(this).val() === undefined) || ($(this).val() === "") )
                valid = false;
            pick_level.push($(this).val());
        });
        data['level-'+i] = pick_level;
    }
    out(data);

    if($(".select.is-danger").length > 0) {
        valid = false;
    }

    if(!valid) {
        window.alert("Please complete entire form or fix errors");
        return;
    }
    button.addClass("is-loading");
    out(data);
    $.ajax({
        url: "/picks/change/save",
        type: "POST",
        data: data,
        success: function (r) {
            out(r);
            button.removeClass("is-loading");
            if(r == '10') {
                window.alert("You have been logged out. Please log back in and try again");
                return;
            }
            if(r == '00') {
                window.alert("Unable to submit. Please fix errors");
                return;
            }
            window.alert("Picks saved successfully. You have been sent a confirmation email");

        },
        error: function(e) {
            console.log(e);
            window.alert("Unable to connect to server. Please try again later");
            button.removeClass("is-loading");
        }
    });

});

$("#delete-pickset-link").click(function() {
    const container = $("#change-picks-container");
    const c = window.confirm("Are you sure you would like to delete the pickset: " + container.data("psname") + "? This action cannot be undone");
    if(!c) {
        return;
    }

    $.ajax({
        url: '/picks/delete',
        type: 'POST',
        data: {"psid": container.data("psid")},
        success: function (r) {
            if(r != '1') {
                window.alert("You have been logged out. Please log back in then try again");
                return;
            }

            window.alert("Successfully deleted pickset");
            window.location.reload();
        },
        error: function(e) {
            console.log(e);
            window.alert("There was an error connecting to server. Please try again later");
        }

    });
});