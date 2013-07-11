$(function() {
    function reloadConversationList() {
        $.ajax("conversations", {
            cache: false,
            success: function (data, textStatus, jqXHR) {
                $("#conversation_list").empty().append(data);
            }
        });
    }

    setInterval(reloadConversationList, globalConfig.UPDATE_INTERVAL);

    reloadConversationList();
});
