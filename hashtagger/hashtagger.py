#!/usr/bin/python

import sys, os
import nltk
import tika
tika.initVM()

from texttable import Texttable
from tika import parser

class FileInterpreter:

  def __init__(self, filename):
    self.filename = filename
    self.content = None
    self.frequent_words = None
    self.sentences_of_frequent_words = None

    self.parse()

  def parse(self):
    # TODO: TRY/CATCH
    if self.filename.endswith('.txt'):
      file = open(self.filename, 'r')
      raw_content = file.read().decode('utf8')
      file.close()
    else:
      file = parser.from_file(self.filename)
      raw_content = file['content']

    self.content = raw_content

  def extract_frequent_words(self, number_of_words=0):
    if not self.content:
      return

    tokenized_words = nltk.tokenize.word_tokenize(self.content.lower())
    english_stopwords = nltk.corpus.stopwords.words('english')

    # Clean words, include only the ones that are more than one character
    # and have alphabetic characters
    clean_tokenized_words = ( w.lower() for w in tokenized_words if w.isalpha() if len(w)>1 if w.lower() not in english_stopwords )

    # Calculate frequency of words
    frequency_words = nltk.FreqDist(w.lower() for w in clean_tokenized_words)

    # If a number of words to return is given (n)
    if (number_of_words):
      # then return the (n) most common words
      self.frequent_words = frequency_words.most_common(number_of_words)
    else:
      # otherwise return all words in ascending order with higher frequency
      self.frequent_words = frequency_words.most_common()

  def extract_sentences_of_frequent_words(self):
    if not self.frequent_words:
      return

    sentences_of_frequent_words = []
    tokenized_sentences = nltk.tokenize.sent_tokenize(self.content)

    for word in self.frequent_words:
      word_matched_sentences = [sentence for sentence in tokenized_sentences if word[0] in nltk.tokenize.word_tokenize(sentence.lower())]
      sentences_of_frequent_words.append(word_matched_sentences)

    self.sentences_of_frequent_words = sentences_of_frequent_words


class Hashtagger:

  def __init__(self, file_interpreters, hashtags_per_doc=0):
    self.file_interpreters = file_interpreters
    self.hashtags_per_doc = hashtags_per_doc
    self.data_structure = {}

    self.extract_hashtags()

  def extract_hashtags(self):
    for file_interpreter in self.file_interpreters:
      if self.hashtags_per_doc:
        file_interpreter.extract_frequent_words(self.hashtags_per_doc)
      else:
        file_interpreter.extract_frequent_words()
      file_interpreter.extract_sentences_of_frequent_words()

      for index in range(0, len(file_interpreter.frequent_words)):
        file = file_interpreter.filename
        word = ( file_interpreter.frequent_words[index][0] ).encode('utf-8')
        freq = file_interpreter.frequent_words[index][1]
        sentences = file_interpreter.sentences_of_frequent_words[index]
        # sentences = '\n '.join([x.encode('utf-8') for x in sentencesList])

        if word in self.data_structure:
          # Add new file
          self.data_structure[word][1] = self.data_structure[word][1] + '\n' + file +' (' + str(freq) + ')'
          # Add new sentences
          self.data_structure[word][2].append(sentences)
        else:
          tmp = [word, file + ' (' + str(freq) + ')', sentences]
          self.data_structure[word] = tmp

  def print_findings(self):
    data = [ ['#','In document (frequency)','Snippet (document)'] ]

    for value in self.data_structure.values():
      data.append(value)

    viewer = Texttable()
    viewer.add_rows(data)
    print '\n' + viewer.draw() + '\n'


def main(argv):

  file_interpreters = []

  template_filepath = argv[0]
  template_filenames = [ (template_filepath + '/' + f) for f in os.listdir( template_filepath ) if not f.startswith('.') ]

  for filename in template_filenames:
    file_interpreters.append( FileInterpreter(filename) )

  hashtagger_obj = Hashtagger( file_interpreters, 10).print_findings()

if __name__ == '__main__':
  main(sys.argv[1:])