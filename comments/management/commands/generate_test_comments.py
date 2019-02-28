from django.core.management.base import BaseCommand, CommandError

from comments.models import Comment, CommentVersion

class Command (BaseCommand):
    help = """Generates a large number of comments for testing."""
    
    def add_arguments(self, parser):
        parser.add_argument('parent_comment_id', nargs='+', type=int)
        parser.add_argument('num_comments', nargs='+', type=int, default=100)

    def handle(self, *args, **options):
        print('Getting parent comment...')
        try:
            parent = Comment.objects.get(id=options['parent_comment_id'][0])
            print("Success")
        except Comment.DoesNotExist:
            raise CommandError('Comment "%s" does not exist' % options['parent_comment_id'][0])
        print('Generating comments...')
        for x in range(0, options['num_comments'][0]):
            comment = Comment(parent=parent)
            Comment.objects.insert_node(comment, parent, save=True)
            CommentVersion.objects.create(comment=comment, message="Comment")
        print("All Done!")