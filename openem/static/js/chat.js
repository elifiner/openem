$(function() {
    var lastMessageId = 0;

    // add a message to history and submit it to the server
    function submitMessage() {
        var text = $("#message").val();
        $("#message").val("");
        $("#history").append(formatMessage(chatConfig.user, chatConfig.userMessageType, text, true));
        // FIXME: doesn't scroll to bottom on Safari, probably works badly on phones
        scrollToBottom();
        $("#message").focus();
        $.post("post", {text:text});
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
                var doScroll = isCloseToBottom();
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
                "unescaped_text": text
            }
        });
    }

    function isCloseToBottom() {
        fromBottom = $(document).height() -  $(window).scrollTop() - $(window).height();
        return (fromBottom < 50);
    }

    function scrollToBottom() {
        $(document).scrollTop($(document).height());
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
