$(function() {
    var app = $('#app'),
        init = $('#init'),
        layer = $('#layer'),
        input = $('#inp-cover input'),
        button = $('button');

    function toggleApp() {
        app.toggleClass('opened');

        if (button.hasClass('shadow'))
            button.toggleClass('shadow');
        else
            setTimeout(function() {
                button.toggleClass('shadow');
            }, 300);

        if (app.hasClass('opened')) {
            setTimeout(function() {
                input.toggleClass('move-up');
            }, 200);
            setTimeout(function() {
                input.focus();
            }, 500);
        } else
            setTimeout(function() {
                input.toggleClass('move-up').val('');
            }, 200);

        if (!layer.hasClass('sl')) {
            setTimeout(function() {
                layer.addClass('sl');
            }, 800);
        } else
            setTimeout(function() {
                layer.removeClass('sl');
            }, 300);
    }

    layer.on('click', toggleApp);
    init.on('click', toggleApp);
});