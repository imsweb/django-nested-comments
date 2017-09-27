========
Comments
========

The django-comments application allows you to associated comment trees with any Django model. It does this without any modification to View or Model
code [#f1]_ . The application works by using an MPTT tree to track a tree of comments. Each comment object has one of two things, either A) the content type
id and pk of a parent object or B) a foreign key to a parent comment.

.. note:: Be careful that the 'parent' object your comment tree is associated is unique enough for your use case.

.. [#f1] While it is not necessary to modify model code it is optional to allow customization, see `Customization`_ .

Template Tags
=============

This app comes with a few built in template tags that allow for simple integration and customization.
    * ``initialize_comments`` - This tag does two things:
        1) It sets default values for some of the javascript settings that need access to Django tags to be populated (ex. URLs)
        2) It filters the 'kwargs' passed in and takes those that do not override javascript settings and puts them in a variable labeled 'kwargs'
    * ``render_comments`` - Renders the initialization template with the content type/id of the parent object.

Customization
=============

Parent Object
-------------

The parent object is the object that is associated with the root comment object via it's content type id and it's PK. Some characteristics of each
comment tree can be overriden by defining values/functions on the parent object's model class.

Values:

    * ``single_comment_template`` - the template to render a single comment (essentially the comment 'form')
    * ``comments_template`` - the template to render the whole comment tree (utilizes 'single_comment_template')
    * ``max_depth`` - The 'depth' of the comments tree (1 based).

Functions:

    * ``can_reply_to_comment(request, comment)`` - Function that returns a boolean. True if the user is allowed to reply to the given comment. 'Reply' means to create a comment that is nested under the given comment.
    * ``can_post_comment(request, comment)`` - Function that returns a boolean. True if the user is allowed to post/edit the given comment. 
    * ``can_delete_comment(request, comment)`` - Function that returns a boolean. True if the user is allowed to delete the given comment.
    
Javascript
----------

When initializing the javascript component of the application the following settings can be overridden (example below). Most of the settings are selectors
for components of the templates used to render the comment tree. They will only need to be overridden if the templates are as well.

    * ``nodeContainerSelector`` - Selector for each node in the tree (including the root and each comment).
    * ``actionTriggerSelector`` - On click, the items with this selector will have their 'action' data value ( $(this).data('action') ) checked for one of the following values:
        * ``post-new`` - Submits the closest comment form as a new comment.
        * ``post-edit`` - Submits the closest comment form to be edited.
        * ``reply`` - Toggles the 'commentFormSelector'.
        * ``edit`` - Toggles the 'originalMessageSelector' and 'messageEditContainerSelector' for the closest 'commentContainerSelector'.
        * ``delete`` - After displaying a confirmation modal, this submits a delete request for the closest comment.
    * ``childCommentsSelector`` - Selector for containers below each comment, except those at max_depth, that contain that comments children as well as the form to add another child comment.
    * ``commentContainerSelector`` - Selector for containers that holds an individual comment.
    * ``commentFormSelector`` - Selector for containers that hold the form fields for a comment (essentially a form).
    * ``hiddenFieldsSelector`` - Selector for containers holding the hidden fields that will be included with http requests. By default these containers are inside 'commentFormSelector' containers.
    * ``messageEditContainerSelector`` - Selector for containers that hold the 'commentFormSelector' containers for an existing comment. This is used to toggle between a comments content and a form to edit it.
    * ``originalMessageSelector`` - Selector for the original comment content for an existing comment (toggles with 'messageEditContainerSelector' to allow edit)
    * ``postCommentUpdatedFunction`` - Callback function that will be executed after a comment is posted, edited, or deleted via ajax.
    * ``postCommentLoadFunction`` - Callback function that will be executed after a comment tree has been loaded via ajax.
    * ``rootContainerSelector`` - Selector for the comment root, which is a container that holds all comments (but NOT the highest level 'hiddenFieldsSelector' object). This is the element that emptied and appended to on each full comment tree load.
    * ``getUrl`` - URL called to load the comment tree.
    * ``postUrl`` - URL called to post/edit a comment.
    * ``deleteUrl`` - URL called to delete a comment.
    
.. note:: There is a 'kwargs' setting that will be passed back verbatim in the 'X-KWARGS' header of all requests. This is usually populated using the 'initialize_comments' template tag and allows the site to pass information back to itself.
    
To override a javascript setting additional settings can be passed in on initialization, ex: ::

    // Settings to be overridden
    var settings_override = {
        'postCommentUpdatedFunction': function(){
            rebuildCKEditors();
        },
    }
    
    // Comments initialization
    $('document.body').comments($.extend({% initialize_comments %}, settings_override));
    
Signals
=======

The django-comments app fires the ``comment_changed`` signal and includes the following information:
    * ``sender`` - the comment that was updated
    * ``request`` - the http request object that caused the change
    * ``comment_action`` - the action that was completed. The following values can be passed:
        1) ``edit`` - An existing comment (the sender) was edited.
        2) ``post`` - A new comment (the sender) was submitted.
        3) ``pre_delete`` - A comment (the sender) is about to be deleted. This action has NOT occurred yet!
    * ``version_saved`` - the CommentVersion object that was just saved (None if the 'comment_action' was a 'pre_delete')
    * ``kwargs`` - Any value passed in via the javascript 'X-KWARGS' header (which in turn was passed in from the 'kwargs' setting).

Class Reference
===============

These class descriptions include all attributes and methods associated with these models (including inherited). Sphinx would not parse docstrings for
specific model fields, so check the model itself for more detail.

.. note:: The 'data' field on the Comment model is a JSON field to allow custom data to be associated with the comment model.
    
.. autoclass:: comments.models.Comment
    :members:
    :inherited-members:
    :undoc-members:
    
.. autoclass:: comments.models.CommentVersion
    :members:
    :inherited-members:
    :undoc-members: