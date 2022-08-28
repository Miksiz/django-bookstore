from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
import json, random, urllib.request
from os.path import basename

from books.models import Book

class Command(BaseCommand):
  help = 'Loads 20 random books from json file to the database'

  def add_arguments(self, parser):
    parser.add_argument('json_file')
  
  def handle(self, *args, **options):
    try:
      with open(options['json_file']) as f:
        file_contents = f.read()
    except:
      raise CommandError('File could not be opened: %s!' % options['json_file'])
    try:
      books_data = json.loads(file_contents)
    except:
      raise CommandError('Could not parse JSON from the file!')
    for _ in range(20):
      book_data = random.choice(books_data)
      try:
        author = ', '.join(book_data['authors'])
        price = str(random.choice(range(10,50)))+'.'+random.choice(['00', '99', '98'])
        image_url = book_data.get('thumbnailUrl', None)
      except:
        self.stderr.write(self.style.ERROR('Could not parse info for book %s' % (repr(book_data))))
        continue
      try:
        image_data = urllib.request.urlretrieve(image_url)
      except:
        self.stderr.write(self.style.ERROR('Could not retrieve image from %s' % (image_url)))
        image_data = None
      try:
        book = Book.objects.create(
          title=book_data['title'],
          author=author,
          price=price
        )
        if image_url and image_data:
          book.cover.save(basename(image_url), File(open(image_data[0], 'rb')))
        book.save()
      except:
        self.stderr.write(self.style.ERROR('Could not save book - %s' % (book_data['title'])))
        continue
      self.stdout.write(self.style.SUCCESS('Book added - %s' % (book_data['title'])))
      
