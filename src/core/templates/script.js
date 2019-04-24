function like(e) {
    e.preventDefault();
    $('.btn-rating').prop("disabled", true);
    var rating = $(this).val();
    var race = $('input[name=race]:checked').val();
    var id = $('#id').val();
    var url = $('#url').val();

    $.ajax({
        url: "like",
        type: "POST",
        data: {
            "id": id,
            "url": url,
            "race": race,
            "rating": rating
        },
        dataType: "json",
        success: function (data) {
            $('#id').val(data['id']);
            $('#url').val(data['url']);
            $('#tinder_image').prop('src', data['url']);
            $('.btn-rating').prop("disabled", false);
        }
    });
}

$(document).ready(function () {
    $('.btn-rating').click(like);
    $(this).keydown(function (e) {
        var key = e.charCode || e.keyCode || 0;

    });
});
