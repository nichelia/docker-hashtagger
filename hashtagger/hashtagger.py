#!/usr/bin/python

import sys, os, urllib, time, logging
import nltk
import tika

tika.initVM()

from texttable import Texttable
from tika import parser

script_name = 'hashtagger.py'
logging.getLogger().setLevel(logging.INFO)

class FileInterpreter:
  """
    Responsible for reading a file,
    using either python io or
    Apache Tika.
    Extracts frequent words and
    the sentences they are found in.
  """

  def __init__(self, filename=''):

    self.filename = filename # Hold filename
    self.content = None # Hold extracted content of file
    self.frequent_words = None # Hold most common occurring words
    # Hold sentences of most common occurring words
    self.sentences_of_frequent_words = None

    if not filename:
      logging.warn('%s:FileInterpreter: Failed to create object,'\
                   ' no filename given', script_name)
    else:
      # Ready to parse file
      self.parse()

  def parse(self):
    """
      File parser.
      Using python io if text file (.txt),
      Apache Tika otherwise.
      Saves contents in variable.
    """
    try:
      if self.filename.endswith('.txt'):
        file = open( self.filename, 'r' )
        raw_content = file.read().decode('utf8')
        file.close()
      else:
        file = parser.from_file( self.filename )
        # Only interested in the content
        raw_content = file['content']
      self.content = raw_content
    except Exception as e:
      logging.warn('%s:FileInterpreter: Failed to read/extract'\
                   'contents from file %s', script_name, self.filename)
      logging.error(e, exc_info=True)
      pass

  def extract_frequent_words(self, number_of_words=0):
    """
      Extract words from content, collect and clean to
      produce most frequent words array. Persist in
      a set of the word along with its frequency.
    """
    if not self.content:
      logging.info('%s:FileInterpreter: Cannot compute frequency '\
                   'of words, file %s content is empty.',
                   script_name, self.filename)
      return

    # Parse content and separate words (tokenise words)
    # To avoid duplicates, we transform them all to lower case.
    tokenized_words = nltk.tokenize.word_tokenize( self.content.lower() )
    # Since we are using English, we use stopwords
    # defined in the english language.
    english_stopwords = nltk.corpus.stopwords.words('english')

    # Clean our word collection.
    # Exclude stopwords, single-character words and
    # non alphabetic.
    clean_tokenized_words = ( w.lower()
                                for w in tokenized_words 
                                  if w.isalpha()
                                    if len(w)>1
                                      if w.lower() not in english_stopwords )

    # Compute frequency of our clean word collection.
    frequency_words = nltk.FreqDist( w.lower()
                                      for w in clean_tokenized_words )

    # If a number of words to return is given (n),
    if (number_of_words):
      # then return the (n) most common words
      self.frequent_words = frequency_words.most_common(number_of_words)
    else:
      # otherwise return all words in ascending order of higher frequency.
      self.frequent_words = frequency_words.most_common()

  def extract_sentences_of_frequent_words(self):
    """
      Extract senteces from content, for each collected
      frequent word, match senteces that include it and
      persist in an array.
    """
    if not self.frequent_words:
      logging.info('%s:FileInterpreter: Cannot find sentences of '\
                   'frequent words, file %s does not have frequent '\
                   'words.', script_name, self.filename)
      return

    sentences_of_frequent_words = []
    # Parse content and separate sentences (tokenise sentences)
    tokenized_sentences = nltk.tokenize.sent_tokenize( self.content )

    # For every word we collected as frequent,
    for word in self.frequent_words:
      # Check if word is included in sentence
      word_matched_sentences = [ sentence
                                  for sentence in tokenized_sentences
                                    if word[0] in nltk.tokenize
                                        .word_tokenize( sentence.lower() ) ]

      sentences_of_frequent_words.append(word_matched_sentences)

    self.sentences_of_frequent_words = sentences_of_frequent_words


class Hashtagger:
  """
    Responsible for extracting hashtags
    from the FileInterpreter objects, merges
    them and generates a table as output.
  """

  def __init__(self, file_interpreters=[], hashtags_per_doc=0):

    self.file_interpreters = file_interpreters
    self.hashtags_per_doc = hashtags_per_doc
    self.data_structure = {}

    if not file_interpreters:
      logging.warn('%s:Hashtagger: Failed to create object,'\
                   ' no file interpreters given', script_name)
    else:
      # Ready to extract hashtags from FileInterpreter objects.
      self.extract_hashtags()

  def extract_hashtags(self):
    """
      Creates a data structure, that includes
      all the words across all the files along with
      the files found in, their frequency and their sentences.
    """

    # For every file,
    for file_interpreter in self.file_interpreters:
      # extract frequent words
      if self.hashtags_per_doc:
        file_interpreter.extract_frequent_words(self.hashtags_per_doc)
      else:
        file_interpreter.extract_frequent_words()

      # and their sentences
      file_interpreter.extract_sentences_of_frequent_words()

      if ( not file_interpreter.frequent_words or
           not file_interpreter.sentences_of_frequent_words ):
        logging.info('%s:Hashtagger: Cannot generate hashtags, '\
                     'frequent words and/or their sentences are '\
                     'missing. (file: %s)',
                     script_name, file_interpreter.filename)
        return

      # For every frequent word,
      for index in range( 0, len(file_interpreter.frequent_words) ):
        # collect filename, word, frequency and sentences it's included.
        file = file_interpreter.filename
        word = ( file_interpreter.frequent_words[index][0] ).encode('utf-8')
        freq = file_interpreter.frequent_words[index][1]
        sentences = file_interpreter.sentences_of_frequent_words[index]

        # Persist in a data structure dictionary.
        if word in self.data_structure:
          # Include new file found
          self.data_structure[word][1] = ( self.data_structure[word][1] + 
                                          '\n' + file + 
                                          ' (' + str(freq) + ')' )
          # Include new sentences found
          self.data_structure[word][2].append(sentences)
        else:
          # Create a new array of format:
          tmp = [ word, file + ' (' + str(freq) + ')', sentences ]
          self.data_structure[word] = tmp

  def print_findings(self):
    """
      Prepare data for a table and display it.
    """

    # Specify our table headers as the first array of data.
    data = [ ['#','In document (frequency)','Snippets'] ]

    if not self.data_structure:
      logging.info('%s:Hashtagger: Cannot print table, '\
                   'data are missing.', script_name)
      return

    # Append arrays to data array.
    for value in self.data_structure.values():
      data.append(value)

    # Using texttable, draw a table with the
    # data array.
    viewer = Texttable()
    viewer.add_rows(data)
    print '\n' + viewer.draw() + '\n'


def main(template_filepath=''):
  """
    Creates FileInterpreter objects for every document
    found in the given directory (template_filepaht).
    Also creates a Hashtagger object to analyse all the
    documents and print out a table with findings.
  """

  file_interpreters = []

  if template_filepath:
    # Ommit any system files starting with '.'
    template_filenames = [ (template_filepath + '/' + f)
                            for f in os.listdir( template_filepath )
                              if not f.startswith('.') ]

    if not template_filenames:
      logging.warn('%s: Directory contains no documents.', script_name)
      return

    # For every document listed,
    # create a file interpreter object.
    for filename in template_filenames:
      file_interpreters.append( FileInterpreter(filename) )

    # Create hashtagger object to handle documents and print results.
    # Hashtagger configured to only extract 
    # the 10 most common occurring words.
    max_words = 10
    hashtagger_obj = Hashtagger( file_interpreters, max_words)
    hashtagger_obj.print_findings()
  else:
    logging.warn('%s: Not directory given.', script_name)


if __name__ == '__main__':
  start_timer = time.time()

  if ( len(sys.argv) != 2 ):
    raise Exception( '\nUsage: python {0:} <template_filepath>'\
                     '\n\twith: <template_filepath> the directory'\
                     'of the documents to apply hashtags to.\n'
                     .format(script_name) )

  main(sys.argv[1])

  end_timer=time.time()
  elapsed_time=end_timer-start_timer
  logging.info('%s: Executed in %f seconds.',
               script_name, elapsed_time)







