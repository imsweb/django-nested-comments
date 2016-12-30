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
        	actionTriggerSelector: ".action-trigger",
        	commentFormSelector: ".comment-form",
        	
        	getUrl: null,
        	
			postUrl: null,
			postCommentSelector: ".post-comment",
			
			deleteUrl: null,
			deleteCommentSelector: ".delete-comment"
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
    			data: $(appContainer).find(':input').serialize(),
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
        
        // TODO: decide how to handle combined/separate design
        $('body').on('click', settings.postCommentSelector, function() {
        	var appContainer = $(this).closest(settings.appContainerSelector);
        	var callback = $.Deferred();
        	callback.always(function(response){
        		$(appContainer).find(settings.treeContainerSelector).empty().append(response.html_content);
        	});
        	post_data(settings.postUrl, appContainer, callback);
        	return false;
        });
        
        $('body').on('click', settings.deleteCommentSelector, function() {
        	var appContainer = $(this).closest(settings.appContainerSelector);
        	var callback = $.Deferred();
        	callback.always(function(response){
        		$(appContainer).find(settings.treeContainerSelector).empty().append(response.html_content);
        	});
        	post_data(settings.postUrl, appContainer, callback);
        	return false;
        });
        
        $('body').on('click', settings.actionTriggerSelector, function() {
        	switch($(this).data('action')) {
        		case 'reply':
        			$(this).closest(settings.appContainerSelector).nextAll(settings.commentFormSelector).first().toggle();
        			break;
        	}
        });
    };
}(jQuery));
