(function($) {
    $.fn.comments = function(options) {
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
        	appContainerSelector: ".comments-app-container",
        	treeContainerSelector: ".comments-tree-container",
        	hiddenFieldsContainerSelector: ".comments-hidden-fields",
        	actionTriggerSelector: ".action-trigger",
        	commentFormSelector: ".comment-form",
        	messageEditContainerSelector: ".message-edit-container",
        	originalMessageSelector: ".original-message",
        	
        	getUrl: null,
        	postUrl: null,
        	deleteUrl: null,
        	
			
        }, options);

        var refresh_comments = function() {
        	$(settings.appContainerSelector).each(function(){
        		var appContainer = this;
        		var hiddenFields = $(appContainer).find(':input')
        		// TODO: Check for load_initial and skip if 0 (save us a hit on the server)
        		$.ajax({
        			url: settings.getUrl,
        			data: hiddenFields.serialize(),
        			success: function(response) {
        				if (response.ok){
        					$(appContainer).find(settings.treeContainerSelector).empty().append(response.html_content);
        				}
        				// TODO: handle failure
        			}
        		});
        	})
        };

        var post_data = function(url, appContainer, callback) {
            $.ajax({
            	type: 'POST',
    			url: url,
    			data: $(appContainer).children(settings.hiddenFieldsContainerSelector).find(':input').serialize(),
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
        
        refresh_comments();
        
        // Group all "click handlers" here
        $('body').on('click', settings.actionTriggerSelector, function() {
        	var appContainer = $(this).closest(settings.appContainerSelector);
        	switch($(this).data('action')) {
        		case 'post':
        			// Copy the message content over to the hidden field
        			$(appContainer).find('input[name=message]').val($(appContainer).find('input[name=message_holder]').val())
        			var callback = $.Deferred();
                	callback.always(function(response){
                		// Refresh from parent comment down
                		$(appContainer).parent().closest(settings.appContainerSelector).empty().append(response.html_content);
                	});
                	post_data(settings.postUrl, appContainer, callback);
                	break;
        		case 'reply':
        			$(appContainer).children(settings.commentFormSelector).first().toggle();
        			break;
        		case 'edit':
        			$(appContainer).find(settings.messageEditContainerSelector).first().toggle();
        			$(appContainer).find(settings.originalMessageSelector).first().toggle();
        			break;
        		case 'delete':
        			if(confirm('Deleting this comment will remove all responses as well. Continue?')){
        				var callback = $.Deferred();
        				callback.done(function(response){
        					$(appContainer).remove();
        				}).fail(function(response){
        					// TODO: Better error handling (customizable?)
        					alert("Comments could not be deleted");
        				});
        				post_data(settings.deleteUrl, appContainer, callback);
        			}
        			break;
        	}
        	return false;
        });
    };
}(jQuery));
