#!/usr/bin/python
# Example input:
# git log -p -U0 --date=raw | python ../collate-author-words.py > ../author_rank

import sys, string, re, math, heapq, sgt, operator
from datetime import datetime
from pprint import pprint

# reads the output of `git log -p -U0 --date=raw`

class CommitRecord:
  def __init__(self):
    self.commit_id = None
    self.author = None
    self.date = None
    self.add_terms = set()
    self.del_terms = set()

replace_punctuation = string.maketrans(
    string.punctuation, ' ' * len(string.punctuation))

def flatten_digits_impl(m):
  if m.group(1):
    return '0x' + 'f' * len(m.group(1))
  else:
    return '9' * len(m.group(2))

# Taken from http://stackoverflow.com/questions/14366401
re_c_string = re.compile(r'''(?x)   # verbose mode
    (?<!\\)    # not preceded by a backslash
    "          # a literal double-quote
    .*?        # 0-or-more characters
    (?<!\\)    # not preceded by a backslash
    "          # a literal double-quote
  ''')

def accumulate_terms(text, tset,
      skipcomment=True, genericstring=True, genericdigit=True):
  if skipcomment:
    if re.match(r'^\s*\* ', text):
      return
    text = text.split('/*')[0]
    text = text.split('//')[0]
  if genericstring:
    text = re.sub(re_c_string, ' $ ', text)
  # text = text.translate(replace_punctuation)
  text = re.sub(r'(->|[<>!=~]+|\|\||&&|\+\+|--|::|[\[\]{}.,;()\-+*/^%&?:\|&])', r' \1 ', text)
  if genericdigit:
    text = re.sub(r'0x([a-fA-F\d]+)|(\d+)', flatten_digits_impl, text)
  tset.update(text.split())

def interesting_file(filename):
  return filename.endswith('.c') or filename.endswith('.h')

def readrecord(inp):
  current_record = None
  old_filename = None
  current_filename = None
  while True:
    line = inp.readline()
    if line is None or line.startswith('commit '):
      if current_record is not None:
        yield current_record
      if line is None:
        return
      current_record = CommitRecord()
      current_record.commit_id = line.split(None, 1)[1].strip()
    elif line.startswith('Author: '):
      current_record.author = line.split(None, 1)[1].split('<', 1)[0].strip()
    elif line.startswith('Date: '):
      current_record.date = int(line.split(None)[1])
      dt = datetime.fromtimestamp(current_record.date)
      current_record.month = (dt.year - 1998) * 12 + (dt.month - 1)
    elif line.startswith('--- '):
      old_filename = line.split(' ', 1)[1].strip()
    elif line.startswith('+++ '):
      current_filename = line.split(' ', 1)[1].strip()
    elif line.startswith('+') and interesting_file(current_filename):
      accumulate_terms(line[1:], current_record.add_terms)
    elif line.startswith('-') and interesting_file(old_filename):
      accumulate_terms(line[1:], current_record.del_terms)

class UnigramModel:
  def __init__(self, d=None):
    self.unigram_counts = {}
    self.total_count = 0
    if d is not None:
      self.update(d)
  def add(self, word):
    self.unigram_counts[word] = self.unigram_counts.get(word, 0) + 1
    self.total_count += 1
  def update(self, words):
    if isinstance(words, UnigramModel):
      for word in words.unigram_counts:
        c = words.unigram_counts[word]
        self.unigram_counts[word] = self.unigram_counts.get(word, 0) + c
        self.total_count += c
    for word in words:
      self.add(word)
  def p(self, word):
    if word not in self.unigram_counts:
      return float(self.unigram_counts['']) / self.total_count
    return float(self.unigram_counts[word]) / self.total_count
  def bits(self, word):
    return -math.log(self.p(word), 2)
  def entropy(self):
    return sum([self.bits(word) * self.p(word) for word in self.unigram_counts])
  def cross_entropy(self, other):
    words = other.unigram_counts
    return sum([self.bits(word) * other.p(word) for word in words])
  def top_words(self, n=10):
    return heapq.nlargest(n, self.unigram_counts, key=self.unigram_counts.get)
  def smooth(self):
    # Smooth with simple Good-Turing.
    smoothed, unk = sgt.simpleGoodTuringProbs(self.unigram_counts)
    self.unigram_counts[''] = unk * self.total_count
    for word in smoothed:
      self.unigram_counts[word] = smoothed[word] * self.total_count

class AuthorData:
  def __init__(self, name):
    self.name = name
    self.language_model = UnigramModel()
    self.document_count = 0
  def add_document(self, words):
    self.language_model.update(words)
    self.document_count += 1
    

language_model = UnigramModel()
author_data = {}
limit = 200000
for rec in readrecord(sys.stdin):
  # pprint(vars(rec))
  if len(rec.add_terms):
    author = rec.author
    if author not in author_data:
      author_data[author] = AuthorData(author)
    ad = author_data[author]
    ad.add_document(rec.add_terms)
    language_model.update(rec.add_terms)
    limit -= 1
    if limit <= 0:
      break

for word in language_model.top_words(30):
  print word, language_model.p(word), "(%f bits)" % language_model.bits(word)
print 'Total entropy', language_model.entropy()
author_rank = sorted([
  (ad, language_model.cross_entropy(ad.language_model))
  for ad in author_data.values()], key=operator.itemgetter(1))
for (ad, xe) in author_rank:
  if ad.document_count >= 10:
    print '%s has cross-entropy %f after %d docs' % (
          ad.name, xe, ad.document_count)
