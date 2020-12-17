function get_random_images(){
    $.ajax({
        url: "/random",
        type: "POST",
        complete: function (res){
            if (res.status === 200) {
                let files = res.responseJSON.files;

                for (let i = 0; i < files.length; i++) {
                    $('.images-preview').eq(i).find('img').attr('src', files[i]["web"]);
                    $('#server_image_' + i).val(files[i]["server"]).trigger("change");
                }
            } else {
                // 404 handler
            }
        }
    });
}

function readURL(input) {
    if (input.files && input.files[0]) {
        let reader = new FileReader(),
            preview = $(input).attr("preview");

        reader.onload = function(e) {
            $('#'+preview).attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]); // convert to base64 string
    }
}

function deRequireCb(elClass) {
    let el = document.getElementsByClassName(elClass),
        atLeastOneChecked = false;

    for (let i = 0; i < el.length; i++) {
        if (el[i].checked === true) {
            atLeastOneChecked = true;
        }
    }

    if (atLeastOneChecked === true) {
        for (let i = 0; i < el.length; i++) {
            el[i].required = false;
        }
    } else {
        for (let i = 0; i < el.length; i++) {
            el[i].required = true;
        }
    }
}

$(document).on("change", "#first_image, #second_image", function (){
    readURL(this);

    let check_elems = [
        ["#first_image", "#first_preview"],
        ["#second_image", "#second_preview"]
    ];

    check_elems.forEach(function (x){
        if ($(x[0]).val() === "") {
            $(x[1]).attr("src", "http://127.0.0.1:8000/static/images/nopreview.png");
        }
    });

    $('.images-input').prop("required", true);
    $('#server_image_1, #server_image_2').val("None").trigger("change");
});

$(document).on("click", ".nn-checkbox", function (){
    deRequireCb($(this).attr("class"));
});

$(document).on("click", ".gallery", function (){
    let popup = $(".popup-container");

    if (popup.is(":visible")) {
        popup.fadeOut(200);
    } else {
        popup.fadeIn(200);
    }
});

$(document).on("click", ".close", function (){
    $(this).parent().fadeOut(200);
});

$(document).on("click", ".gallery-item", function (){
    let el = $(this),
        items = el.find("div");

    for (let i = 0; i < items.length; i++) {
        $('.images-preview').eq(i).find('img').attr('src', $(items[i]).find("img").attr("src"));
        $('#server_image_' + i).val($(items[i]).attr("server_image")).trigger("change");
    }

    $('.images-input').val("").prop("required", false);
    $(".close").trigger("click");
});



$(document).on("change", "#random-chose", function (){
    if ($(this).prop("checked")) {
        $('.images-input').hide().val("").prop("required", false);
        get_random_images();
    } else {
        $('.images-input').show().prop("required", true);
        $('.images-preview').find('img').attr("src", "http://127.0.0.1:8000/static/images/nopreview.png");
        $('#server_image_1, #server_image_2').val("None").trigger("change");
    }
});


