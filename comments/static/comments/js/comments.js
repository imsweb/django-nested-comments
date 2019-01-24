(function($) {
    $.fn.comments = function(options) {
        // Copied from Django docs, used to pass in CSRF token
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                 }
            }
            return cookieValue;
        }
        var csrftoken = getCookie('csrftoken');

        // These are mirrored in the 'initialize_comments' template tag. Any change here should be reflected there.
        var settings = $.extend({
            actionTriggerSelector: ".action-trigger",
            childCommentsSelector: ".child-comments",
            commentContainerSelector: ".comment-container",
            commentFormSelector: ".comment-form",
            hiddenFieldsSelector: ".comment-hidden-fields",
            messageEditContainerSelector: ".message-edit-container",
            nodeContainerSelector: ".comments-node-container",
            originalMessageSelector: ".original-message",
            deleteCommentFunction: function(settings, nodeContainer, commentContainer) {
                var confirmationMessage = 'Are you sure you want to delete this comment?';
                var hasChildren = nodeContainer.children(settings.childCommentsSelector).children(settings.nodeContainerSelector).length > 0;
                if (hasChildren) {
                    confirmationMessage += " NOTE: Deleting this comment will remove ALL RESPONSES to this comment as well."
                }
                if(confirm(confirmationMessage)){
                    var callback = $.Deferred();
                    callback.done(function(response){
                        settings.postCommentDeleteFunction(settings, nodeContainer, response);
                        settings.postCommentUpdatedFunction(settings, response);
                    }).fail(function(response){
                        // TODO: Better error handling (customizable?)
                        alert("Comments could not be deleted");
                    });
                    var dataContainer = commentContainer.find(settings.hiddenFieldsSelector);
                    settings.post_data(settings.deleteUrl, dataContainer, callback);
                }
            },
            replyCommentFunction: function(settings, nodeContainer, commentContainer) {
                nodeContainer.children(settings.childCommentsSelector).children(settings.commentFormSelector).toggle();
            },
            post_data: function(url, dataContainer, callback) {
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: $(dataContainer).find(':input').serialize(),
                    settings: settings,
                    beforeSend: function(xhr) {
                        if (!this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                        xhr.setRequestHeader('X-KWARGS', JSON.stringify(settings.kwargs));
                    },
                    success: function(response) {
                        if (response.ok){
                            callback.resolve(response);
                        } else {
                            callback.reject(response);
                        }
                    }
                });
            },
            preCommentLoadFunction: function(settings) {},
            postCommentUpdatedFunction: function(settings, response){},
            postCommentLoadFunction: function(settings, response){},
            postCommentDeleteFunction: function(settings, nodeContainer, response) {$(nodeContainer).remove();},
            rootContainerSelector: ".comments-root-container",
            
            kwargs: {},
            
            getUrl: null,
            postUrl: null,
            deleteUrl: null,
        }, options);

        var load_comments = function() {
            $(settings.nodeContainerSelector).each(function(){
                var nodeContainer = this;
                // TODO: Check for load_initial and skip if 0 (save us a hit on the server)
                $.ajax({
                    url: settings.getUrl,
                    beforeSend: function(xhr) {
                        settings.preCommentLoadFunction(settings);
                        xhr.setRequestHeader('X-KWARGS', JSON.stringify(settings.kwargs));
                    },
                    data: $(nodeContainer).children(settings.hiddenFieldsSelector).find(':input').serialize(),
                    settings: settings,
                    success: function(response) {
                        if (response.ok){
                            $(nodeContainer).find(settings.rootContainerSelector).empty().append(response.html_content);
                            settings.postCommentLoadFunction(settings);
                        }
                        // TODO: handle failure
                    }
                });
            });
        };
        
        // Group all "click handlers" here
        $('body').on('click', settings.actionTriggerSelector, function() {
            var nodeContainer = $(this).closest(settings.nodeContainerSelector);
            var commentContainer = nodeContainer.children(settings.commentContainerSelector).first();
            switch($(this).data('action')) {
                case 'post-new':
                    var commentForm = $(this).closest(settings.commentFormSelector);

                    // Copy the message content over to the hidden field
                    var message_holder = commentForm.find('[name=message_holder]')
                    commentForm.find('input[name=message]').val(message_holder.val());
                    message_holder.val('');

                    var callback = $.Deferred();
                    // TODO: Better error handling (customizable?)
                    // Insert new comment directly before the comment form
                    callback.done(function(response){
                        $(commentForm).before(response.html_content);
                        $(commentForm).toggle();
                        settings.postCommentUpdatedFunction(settings, response);
                    });
                    var dataContainer = commentForm.children(settings.hiddenFieldsSelector);
                    settings.post_data(settings.postUrl, dataContainer, callback);
                    break;
                case 'post-edit':
                    var commentForm = $(this).closest(settings.commentFormSelector);

                    // Copy the message content over to the hidden field
                    var message_holder = commentForm.find('[name=message_holder]')
                    commentForm.find('input[name=message]').val(message_holder.val());
                    message_holder.val('');

                    var callback = $.Deferred();
                    // TODO: Better error handling (customizable?)
                    callback.done(function(response){
                        // Replace the comment being edited with the new version
                        commentContainer.empty().replaceWith(response.html_content);
                        settings.postCommentUpdatedFunction(settings, response);
                    });
                    var dataContainer = commentForm.children(settings.hiddenFieldsSelector);
                    settings.post_data(settings.postUrl, dataContainer, callback);
                    break;
                case 'reply':
                    settings.replyCommentFunction(settings, nodeContainer, commentContainer);
                    break;
                case 'edit':
                    commentContainer.find(settings.originalMessageSelector).first().toggle();
                    commentContainer.find(settings.messageEditContainerSelector).first().toggle();
                    break;
                case 'delete':
                    settings.deleteCommentFunction(settings, nodeContainer, commentContainer);
                    break;
            }
            return false;
        });
        
        load_comments();
        
    };
}(jQuery));
