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
        if (csrftoken == null) {
            csrftoken = $("[name=csrfmiddlewaretoken]").val();
        }

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
            originalMessageExtraSelector: ".original-message-extra",
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
                    	settings.handlePostError(settings, response);
                    });
                    settings.post_data(settings.deleteUrl, settings.getData(settings, commentContainer), callback);
                }
            },
            replyCommentFunction: function(settings, nodeContainer, commentContainer) {
                nodeContainer.children(settings.childCommentsSelector).children(settings.commentFormSelector).toggle();
            },
            editCommentFunction: function(settings, nodeContainer, commentContainer) {
                commentContainer.find(settings.originalMessageSelector).first().toggle();
                commentContainer.find(settings.originalMessageExtraSelector).toggle();
                commentContainer.find(settings.messageEditContainerSelector).first().toggle();
            },
            getData: function(settings, commentContainer) {
            	var dataContainer = commentContainer.find(settings.hiddenFieldsSelector);
            	return $(dataContainer).find(':input').serializeArray();
            },
            handlePostError: function(settings, response) {
            	// override as needed for better error handling
            	if (response.error_message) {
            		alert(response.error_message);
            	}
            	else 
            		alert('An error occurred with your submission. Please try again.');
            },
            handleLoadError: function(settings, response) {
                settings.handlePostError(settings, response);
            },
            post_data: function(url, data, callback) {
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: $.param(data),
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
            postCommentLoadFunction: function(settings, response, nodeContainer){},
            postCommentDeleteFunction: function(settings, nodeContainer, response) {$(nodeContainer).remove();},
            getExtraDataForPost: function(commentFormContainer){return '';},
            commentPostFailExtraCallbacks: function(settings) {return [];},
            copyTextareaData: function(settings, commentForm) {
                // Copy the message content over to the hidden field
                var message_holder = commentForm.find('[name=message_holder]')
                commentForm.find('input[name=message]').val(message_holder.val());
                message_holder.val('');
            },
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
                    cache: false,
                    beforeSend: function(xhr) {
                        settings.preCommentLoadFunction(settings);
                        xhr.setRequestHeader('X-KWARGS', JSON.stringify(settings.kwargs));
                    },
                    data: $(nodeContainer).find(settings.hiddenFieldsSelector).find(':input').serialize(),
                    settings: settings,
                    success: function(response) {
                        if (response.ok){
                            $(nodeContainer).find(settings.rootContainerSelector).empty().append(response.html_content);
                            settings.postCommentLoadFunction(settings, response, nodeContainer);
                        } else {
                            settings.handleLoadError(settings, response);
                        }
                        
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

                    settings.copyTextareaData(settings, commentForm);

                    var callback = $.Deferred();
                    // Insert new comment directly before the comment form
                    callback.done(function(response){
                        $(commentForm).before(response.html_content);
                        // Only hide the commentForm if the form is for a non-root (because there is no toggle button for the root Comment Form)
                        if ($(commentForm).hasClass('non-root')) {
                            $(commentForm).toggle();
                        }
                        settings.postCommentUpdatedFunction(settings, response);
                    });
                	callback.fail(function(response) {
                    	// reset comment msg back
                    	message_holder.val(commentForm.find('input[name=message]').val());
                    	settings.handlePostError(settings, response);
                	});
                    settings.post_data(settings.postUrl, settings.getData(settings, commentForm), callback);
                    break;
                case 'post-edit':
                    var commentForm = $(this).closest(settings.commentFormSelector);

                    settings.copyTextareaData(settings, commentForm);

                    var callback = $.Deferred();
                    callback.done(function(response){
                        // Replace the comment being edited with the new version
                        commentContainer.empty().replaceWith(response.html_content);
                        settings.postCommentUpdatedFunction(settings, response);
                    });
                	callback.fail(function(response) {
                    	// reset comment msg back
                    	message_holder.val(commentForm.find('input[name=message]').val());
                    	settings.handlePostError(settings, response);
                	});
                    settings.post_data(settings.postUrl, settings.getData(settings, commentForm), callback);
                    break;
                case 'reply':
                    settings.replyCommentFunction(settings, nodeContainer, commentContainer);
                    break;
                case 'edit':
                    settings.editCommentFunction(settings, nodeContainer, commentContainer);
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
