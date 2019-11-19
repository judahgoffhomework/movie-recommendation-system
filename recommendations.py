'''
From "Programming Collective Intelligence" by Toby Segaran 
Modifications by Frank McCown

'''

# A dictionary of movie critics and their ratings of a small
# set of movies
from math import sqrt
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


# Returns a Euclidean distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # If they have no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) 
		for item in prefs[person1] if item in prefs[person2]])

    return 1/(1+sqrt(sum_of_squares))


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # Find number of elements
    n = len(si)

    # If no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2)/n) * (sum2Sq - pow(sum2, 2)/n))
    if den == 0:
        return 0

    return num / den


# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    scores.sort(reverse=True)
    return scores[0:n]


# Gets recommendations for a person by using a weighted average
# of every other user's rankings. Returns a list sorted by rankings.
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # Don't compare me to myself
        if other == person:
            continue
        sim = similarity(prefs, person, other)

        # Ignore scores of zero or lower
        if sim <= 0:
            continue

        for item in prefs[other]:
            # Only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item]*sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort(reverse=True)
    return rankings


# Return an inverted matrix, flipping item and person
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


# Return a dictionary of n items showing which items are most similar
def calculateSimilarItems(prefs, n=10):
    result = {}

    print("Calculating similar items...")

    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0:
            print("{0:d} / {1:d}".format(c, len(itemPrefs)))

        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


# Return list of items from itemMatch, sorted by rankings, that are similar
# to the user's prefs
def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():

        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings:
                continue

            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    rankings = [(score / totalSim[item], item) for item, score in scores.items()]

    # Return the rankings from highest to lowest
    rankings.sort(reverse=True)
    return rankings


# Return dict of userIds, each entry is dict of movie titles and ratings
def loadMovieLens(path='movielens'):
    # Get movie titles
    movies = {}
    with open(path + '/movies.csv', encoding="utf8") as movieFile:
        # Ignore first line
        movieFile.readline()

        for line in movieFile:
            # Ignore genre
            (movieid, title) = line.split(',')[0:2]
            movies[movieid] = title

    # Load ratings data
    ratings = {}
    with open(path + '/ratings.csv', encoding="utf8") as ratingFile:
        # Ignore first line
        ratingFile.readline()

        for line in ratingFile:
			# Ignore timestamp
            (userId, movieId, rating) = line.split(',')[0:3]
            ratings.setdefault(userId, {})
            ratings[userId][movies[movieId]] = float(rating)

    return ratings


print("Rose and Seymour =", sim_distance(critics, 'Lisa Rose', 'Gene Seymour'))
print("Toby and LaSalle = ", sim_distance(critics, 'Toby', 'Mick LaSalle'))

print("Rose and Seymour =", sim_pearson(critics, 'Lisa Rose', 'Gene Seymour'))
print("Toby and LaSalle = ", sim_pearson(critics, 'Toby', 'Mick LaSalle'))

print("\nReccommendations for Toby:\n",
      getRecommendations(critics, 'Toby'))

movies = transformPrefs(critics)
print("\nTop Matches for 'Superman Returns':\n",
      topMatches(movies, 'Superman Returns'))

print("\nRecommendations for 'Just My Luck':\n",
      getRecommendations(movies, 'Just My Luck'))

prefs = loadMovieLens()
user = '67'
print(prefs[user])
print(f"\nRecommendations for {user}:\n", getRecommendations(prefs, user)[0:5])

itemsim = calculateSimilarItems(prefs, n=5)
print(f"\nRecommended items for {user}:\n",
      getRecommendedItems(prefs, itemsim, user))
