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
    	
        var settings = $.extend({
        	actionTriggerSelector: ".action-trigger",
        	childCommentsSelector: ".child-comments",
        	commentContainerSelector: ".comment-container",
        	commentFormSelector: ".comment-form",
        	hiddenFieldsSelector: ".comment-hidden-fields",
        	messageEditContainerSelector: ".message-edit-container",
        	nodeContainerSelector: ".comments-node-container",
        	originalMessageSelector: ".original-message",
        	rootContainerSelector: ".comments-root-container",
        	
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
        			data: $(nodeContainer).children(settings.hiddenFieldsSelector).find(':input').serialize(),
        			success: function(response) {
        				if (response.ok){
        					$(nodeContainer).find(settings.rootContainerSelector).empty().append(response.html_content);
        				}
        				// TODO: handle failure
        			}
        		});
        	})
        };

        var post_data = function(url, dataContainer, callback) {
            $.ajax({
            	type: 'POST',
    			url: url,
    			data: $(dataContainer).find(':input').serialize(),
    			beforeSend: function(xhr, settings) {
    		        if (!this.crossDomain) {
    		            xhr.setRequestHeader("X-CSRFToken", csrftoken);
    		        }
    		    },
    			success: function(response) {
    				if (response.ok){
    					callback.resolve(response);
    				} else {
    					callback.reject(response);
    				}
    			}
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
        			var message_holder = commentForm.find('input[name=message_holder]')
        			commentForm.find('input[name=message]').val(message_holder.val());
        			message_holder.val('');
        			
        			var callback = $.Deferred();
        			// TODO: Better error handling (customizable?)
        			// Insert new comment directly before the comment form
                	callback.done(function(response){
                		$(commentForm).before(response.html_content);
                	});
                	var dataContainer = commentForm.children(settings.hiddenFieldsSelector);
                	post_data(settings.postUrl, dataContainer, callback);
                	break;
        		case 'post-edit':
        			var commentForm = $(this).closest(settings.commentFormSelector);
        			
        			// Copy the message content over to the hidden field
        			var message_holder = commentForm.find('input[name=message_holder]')
        			commentForm.find('input[name=message]').val(message_holder.val());
        			message_holder.val('');
        			
    				var callback = $.Deferred();
    				// TODO: Better error handling (customizable?)
    				callback.done(function(response){
    					// Replace the comment being edited with the new version
            			commentContainer.empty().append(response.html_content);
    				});
    				var dataContainer = commentForm.children(settings.hiddenFieldsSelector);
    				post_data(settings.postUrl, dataContainer, callback);
        			break;
        		case 'reply':
        			nodeContainer.children(settings.childCommentsSelector).children(settings.commentFormSelector).toggle();
        			break;
        		case 'edit':
        			commentContainer.find(settings.originalMessageSelector).first().toggle();
        			commentContainer.find(settings.messageEditContainerSelector).first().toggle();
        			break;
        		case 'delete':
        			if(confirm('Deleting this comment will remove all responses as well. Continue?')){
        				var callback = $.Deferred();
        				callback.done(function(response){
        					$(nodeContainer).remove();
        				}).fail(function(response){
        					// TODO: Better error handling (customizable?)
        					alert("Comments could not be deleted");
        				});
        				var dataContainer = commentContainer.find(settings.hiddenFieldsSelector);
        				post_data(settings.deleteUrl, dataContainer, callback);
        			}
        			break;
        	}
        	return false;
        });
        
        load_comments();
        
    };
}(jQuery));
