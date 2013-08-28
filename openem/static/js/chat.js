$(function() {
    var lastMessageId = 0;

    // converts a multiline string to paragraphs
    function multilineToP(text) {
        text = $('<div/>').text(text).html(); // escaping
        var lines = text.split(/\r?\n/);
        for (var i = 0; i < lines.length; i++) {
            if (lines[i].trim()) {
                lines[i] = '<p>' + lines[i] + '</p>';
            }
        }
        return lines.join('\n');
    }

    // add a message to history and submit it to the server
    function submitMessage() {
        var message = $("#message").val();
        $("#message").val("");
        $("#history").append(formatMessage(chatConfig.user, chatConfig.userMessageType, multilineToP(message), true));
        $("#message").height(0); // relies on min-height to set actual height
        scrollToBottom();
        $("#message").focus();
        $.post("post", {
            message : message, // escaping is done on the backend
            csrfmiddlewaretoken: chatConfig.csrfToken
        });
    }

    // get message updates from the server
    var reloading = false; // prevent multiple ajax calls from going out at the same time
    function updateHistory() {
        if (reloading) {
            return;
        }
        reloading = true;
        $.ajax("updates", {
            data: { last_message_id: chatConfig.lastMessageId },
            success: function (data, textStatus, jqXHR) {
                chatConfig.lastMessageId = data.last_message_id;
                var doScroll = (data.messages.length > 0);
                $.each(data.messages, function (index, message) {
                    $("#history").append(formatMessage(message.author, message.type, message.unescaped_text, false));
                });
                if (doScroll) {
                    scrollToBottom();
                }
            },
            complete: function () {
                reloading = false;
            }
        });
    }

    var messageTemplate = Handlebars.compile($("#message-template").html());
    function formatMessage(author, type, text, escape) {
        return messageTemplate({
            "message" : {
                "type" : type,
                "author" : {
                    "name" : author
                },
                "post_time_since" : "רגע",
                "html_text": new Handlebars.SafeString(text)
            }
        });
    }

    function isCloseToBottom() {
        fromBottom = $(document).height() -  $(window).scrollTop() - $(window).height();
        return (fromBottom < 50);
    }

    function scrollToBottom() {
        $("html,body").scrollTop($("#bottom").offset().top - $(window).height());
    }

    $("#message_form").submit(function(e) {
        e.preventDefault();
        submitMessage();
    });

    // start periodic updates
    setInterval(updateHistory, globalConfig.UPDATE_INTERVAL);

    // when page is reloaded scroll to the bottom if already there
    if (isCloseToBottom()) {
        scrollToBottom();
    }
});
