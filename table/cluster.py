import numpy as np
from sklearn.cluster import KMeans

def  big_s(x, center):
    len_x = len(x)
    total = 0
    for i in range(len_x):
        total += np.linalg.norm(x[i]-center)
    return total/len_x


def davisbouldin(k_list, k_centers):
    """ Davis Bouldin Index
    Parameters
    ----------
    k_list : list of np.arrays
        A list containing a numpy array for each cluster |c| = number of
        clusters
        c[K] is np.array([N, p]) with:
          - N : number of samples in cluster K
          - p : sample dimension
    k_centers : np.array
        The array of the cluster centers (prototypes) of type np.array([K, p])
    """
    len_k_list = len(k_list)
    big_ss = np.zeros([len_k_list], dtype=np.float64)
    d_eucs = np.zeros([len_k_list, len_k_list], dtype=np.float64)
    db = 0

    for k in range(len_k_list):
        big_ss[k] = big_s(k_list[k], k_centers[k])

    for k in range(len_k_list):
        for l in range(0, len_k_list):
            d_eucs[k, l] = np.linalg.norm(k_centers[k]-k_centers[l])

    if len_k_list > 1:
        for k in range(len_k_list):
            values = np.zeros([len_k_list-1], dtype=np.float64)
            for l in range(0, k):
                values[l] = (big_ss[k] + big_ss[l])/d_eucs[k, l]
            for l in range(k+1, len_k_list):
                values[l-1] = (big_ss[k] + big_ss[l])/d_eucs[k, l]

            db += np.max(values)
    else:
        db = big_ss[0]
        len_k_list = 1
    res = db/len_k_list
    return res


def bestKMeansByTransform(coordinates, k, fn, params):
    """
    Finds the best param to fit the data using KMeans and
    'Davis Bouldin Index' as an internal evaluation metric.
    """
    bestParam = 0
    bestIndex = 10000000
    bestClusters = []
    bestCenters = []
    improved = False
    for param in params:
        Y = np.array([fn(x, y, param)[1] for x, y in coordinates])
        Y = Y.reshape((-1, 1))
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(Y)
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        clusters = []
        for c in centers:
            clusters.append([])
        for index, l in enumerate(labels):
            clusters[l].append([Y[index][0]])
        index = davisbouldin(clusters, centers)
        if index < bestIndex:
            bestIndex = davisbouldin(clusters, centers)
            bestParam = param
            bestClusters = kmeans.predict(Y)
            bestCenters = centers
    return bestClusters, bestCenters, bestParam


def bestKMeansByK(coordinates, maxClusters=9, minClusters=1):
    """
    Finds the best cluster number k to fit the data using KMeans and
    'Davis Bouldin Index' as an internal evaluation metric.
    """
    bestIndex = 10000000
    bestClusters = []
    bestCenters = []
    improved = False
    X = np.array(coordinates)
    X = X.reshape((-1, 1))
    M = min(maxClusters, len(coordinates) + 1)
    for i in xrange(minClusters, M):
        kmeans = KMeans(n_clusters=i, random_state=0)
        kmeans.fit(X)
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        clusters = []
        for c in centers:
            clusters.append([])
        for index, l in enumerate(labels):
            clusters[l].append([X[index][0]])
        if np.any([len(x) == 0 for x in clusters]):
            continue
        index = davisbouldin(clusters, centers)
        if index < bestIndex:
            bestIndex = davisbouldin(clusters, centers)
            bestK = i
            bestClusters = kmeans.predict(X)
            bestCenters = centers
    return bestClusters, bestCenters
