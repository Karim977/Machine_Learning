import os
import random
import re
import sys
import math
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    x = {}
    N = len(corpus)
    Y = (1 - damping_factor) / N
    if len(corpus[page]) != 0:
        Z = damping_factor / len(corpus[page])
    F = damping_factor / N
    # Iterating along all keys (pages) in the dictionary
    for p in corpus:
        if len(corpus[page]) == 0:
            x[p] = Y + F
        # If it's the page itself then it shares a prob of the (1-d) divided equally among ALL pages
        if p == page:
            x[p] = Y
        # If this page was a link in the page that we're sampling, then it holds a share of damping while shared on its neighbour links in the same page AND a share of the (1-d) probability
        # If I was in page 1 and it links to page 2 and 3 , then the probability to go to page 2 is by randomly picking page 2 with a share of the prob of (1-d) OR
        # just clicking the link because I'm on page 1 now and it has a link to page 2 and this has a higher probability of d but shared equally on all links in page 1
        # The original method was to share all the probabilities = 1 equally on the links of page 1 not sharing only 0.85 on the links
        # We did so because if page 2 linked to page 3 and page 3 linked to page 2, they would loop ininitely over each other if the prob of 1 was shared equally between their links which are '2' and '3'
        # So we added LOW possibility that the loop would be broken by this low possibility and therefore exit the infinite loop
        elif p in corpus[page]:
            x[p] = Y + Z
        # If it was a page that wasn't in the links of the given page, then the prob that it will be clicked is 1-d but shared equally between all the links so (1-d) / Number of links
        else:
            x[p] = Y
    return x


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    x = {}
    P = []
    V = []
    sample = random.choice(list(corpus.keys()))
    x[sample] = 1
    for i in range(n-1):
        # Transition model applied to that sample, if it was the first sample then it's applied on it, then this sample is substituted by the randomly (WEIGHTED) picked sample
        T_M = transition_model(corpus, sample, damping_factor)
        # 'P' array contains all pages , 'V' array contains all corresponding probability that this page is picked upon the sample random choice afterwards
        P = list(T_M.keys())
        V = list(T_M.values())
        # A sample is generated using a random WEIGHTED method depending on all the probabilities of the upcoming pages to be picked from
        sample = random.choices(population = P, weights = V)[0]
        x[sample] = x.get(sample, 0) + 1
    for k, v in x.items():
        x[k] = v / n
    return x

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    x = {}
    old = {}

    # Recursive function to calculate PageRank of a given page
    def PR(P, C):
        # It's efficient to loop on a LIST of dict keys instead on the keys bec if we removed an item in the dictionary, it will produce an error
        # This list is constantly changing size with the new corpus after removing an element from it
        for page in list(C):
            if P in C[page]:
                n = len(C[page])
                del C[page]
                return ( old[page] / n ) + PR(P, C)
            elif len(C[page]) == 0:
                del C[page]
                return ( old[page] / len(corpus) ) + PR(P, C)
            del C[page]
        # Condition where the recursion stops
        return 0

    d = 0.85
    N = len(corpus)
    for c in corpus:
        x[c] = 1 / len(corpus)
        old[c] = x[c]
    # Now x values are identical to old so we must do this flag in order to enter the loop once and then it will loop purely on the condition
    flag = True

    # while any(abs(old[p] - x[p]) > 0.001 for p in corpus):
    while any(abs(old[p] - x[p]) > 0.001 for p in corpus) or flag:
        flag = False
        for p in corpus:
            # Assigning values in x[p] 'Page ranks' to old because we're going to alter it downwards with the equation
            old[p] = x[p]
        for P in corpus:
            # Taking a deepcopy of corpus bec we'll eventually remove elements from it
            C = copy.deepcopy(corpus)
            x[P] = ( (1 - d) / N ) + d * ( PR(P, C) )

    return x

if __name__ == "__main__":
    main()
