function rgbToHex(color) {
    var rgb = /rgb\((\d+)\,\s(\d+)\,\s(\d+)\)/g.exec(color),
        r = parseInt(rgb[1]),
        g = parseInt(rgb[2]),
        b = parseInt(rgb[3]);

    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

$('.colors button').on('click', function (event) {
    event.preventDefault();

    var color = $(this).css('background-color');

    $('.colors_current').css('background-color', color);
    $('.colors input[name="color"]').val(rgbToHex(color));
});
