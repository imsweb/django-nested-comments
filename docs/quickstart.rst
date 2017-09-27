Quickstart Guide
================

1. Add ``comments`` to your ``INSTALLED_APPS`` setting and run migrations.

.. highlight:: html+django

2. Include ``comments/js/comments.js`` in the pages you want to display/update comments on::

        {% load static %}
        <script src="{% static "comments/js/comments.js" %}"></script>

3. Import the comments app templatetags and initialize the comments section (passing in the object to associate them with)::

        {% load comments %}
        {% render_comments obj_to_attach_comments_to %}

.. highlight:: js+django

4. Initialize the comments code ('settings_override' is optional and displayed here as an example)::

        var settings_override = {
            'postCommentUpdatedFunction': function(){
                rebuildCKEditors();
            },
        }
        $('document.body').comments($.extend({% initialize_comments %}, settings_override));
        
5. (OPTIONAL) Certain configurations are available when set on the 'obj_to_attach_comments_to' model (from step 3). See :ref:`Customization` .
