(function ($) {
    // automatically resizes a textarea when user types more that it can contain
    // also scrolls to the bottom of the screen

    $.fn.autoResize = function() {
        el = this;
        el.css("overflow", "hidden");
        hidden = $("<div/>").hide()
            .css("width", el.css("width"))
            .css("font", el.css("font"))
            .css("line-height", el.css("line-height"))
            .css("min-height", el.css("min-height"))
            .css("padding", el.css("padding"))
            .css("border", el.css("border"))
            ;
        $("body").append(hidden);

        function updateHeight(scroll) {
            value = el.val().replace(/\n *$/, "\nM").replace(/\n/g, "<br>");
            if (value === "") value = "M";
            hidden.html(value);
            el.height(hidden.height());
            if (scroll) {
                $('html,body').scrollTop($(document).height() - $(window).height());
            }
        }

        updateHeight(false);

        $(el).on("keydown cut paste update", function () {
            setTimeout(function() { updateHeight(true); }, 0);
        });
    };
}) (jQuery);
