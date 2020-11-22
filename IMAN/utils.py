def zip_longest(iterable1, iterable2):
  """
  The .next() method continues until the longest iterable is exhausted.
  Till then the shorter iterable starts over.
  """
  iter1, iter2 = iter(iterable1), iter(iterable2)

  iter1_exhausted = iter2_exhausted = False

  while not (iter1_exhausted and iter2_exhausted):
    try:
      el1 = next(iter1)
    except StopIteration:
      iter1_exhausted = True
      iter1 = iter(iterable1)
      continue
    try:
      el2 = next(iter2)
    except StopIteration:
      iter2_exhausted = True
      if iter1_exhausted:
        break
      iter2 = iter(iterable2)
      el2 = next(iter2)

    yield el1, el2
