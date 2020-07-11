import torch
import os
from gensim.models import FastText, Word2Vec, Doc2Vec
import numpy as np
from scipy.io import loadmat
import networkx as nx
from networkx import laplacian_matrix, normalized_laplacian_matrix
from get_neighbors import load_neighbors

NODES = set()
DEGREE = {}

def load_embeddings(filename, split, emb_dims):
    # print(filename, split)
    model = Doc2Vec.load("../data/par2vec/{0}/split{1}.model".format(filename, split))
    #model = Doc2Vec.load("../par2vec_new/{0}/split{1}_iter100_n50_top10_wass_p0.4_hop2_w10.model".format(filename, split))
    #model = Doc2Vec.load("../par2vec_new/Sensitivity/{0}/split{1}_iter50_n50_knn40_top10_wass_p0.4_w5.model".format(filename, split))
    embeddings = []
    for node in range(0,max(NODES)+1):
        try:
            emb = model[str(node)]
            #print("sum of embedding:",sum(emb))
            embeddings.append(emb)
        except:
            continue

    embeddings = np.array(embeddings).astype(np.float32)
    #print(embeddings.shape)
    #for i in range(0,10):
        #print("sum of embedding:",sum(embeddings[:,i]))

    #exit()
    #embeddings = np.random.rand(len(embeddings), len(embeddings[0]))
    return embeddings

def get_laplacian(dataset_name):
    x = loadmat('../data/mat_versions/{}.mat'.format(dataset_name))
    b = x['net']
    adjacency = b.toarray()
    degrees = []
    for i in range(len(NODES)):
        degrees.append(DEGREE[i])
    degree_matrix = np.diag(degrees)
    # print(degree_matrix)
    # print(adjacency)
    return degree_matrix - adjacency

def parse_line(line):
    line = line.strip().split()
    e1, e2 = line[0].strip(), line[1].strip()
    return e1, e2

def load_data_from_file(filename, get_degree):
    with open(filename) as f:
        lines = f.readlines()

    rows, cols = [], []
    edge_data = []

    for line in lines:
        e1, e2 = parse_line(line)
        e1 = int(e1)
        e2 = int(e2)

        # if e1 not in DEGREE.keys():
        #     DEGREE[e1] = 1
        # else:
        #     DEGREE[e1] += 1
        if get_degree:
            if e2 not in DEGREE.keys():
                DEGREE[e2] = 1
            else:
                DEGREE[e2] += 1
        
        NODES.add(e1)
        NODES.add(e2)
        # unique_entities.add(e1)
        # unique_entities.add(e2)
        edge_data.append((e1, e2))
        
        # Connecting tail and source entity
        rows.append(e2)
        cols.append(e1)
        
    return edge_data, (rows, cols)

def getL(train_adjacency_mat,num_nodes):
	G = np.zeros((num_nodes,num_nodes),dtype = int)
	row, col = train_adjacency_mat
	G[row, col] = 1
	G[col, row] = 1
	A = np.matrix(G)
	G = nx.from_numpy_matrix(A)
	N = normalized_laplacian_matrix(G)
	return N.toarray()

def load_spectrum(dataset_name):
    mat = np.load("../Spectrum/" + dataset_name + ".npy")
    # print(mat.shape)
    return mat

def build_data(dataset_name, split,emb_dims):
    path='../data/Splits/{0}/{1}'.format(dataset_name, split)
    path1='../data/Splits/{0}/{1}'.format(dataset_name,split)
    train_edge_data, train_adjacency_mat = load_data_from_file(os.path.join(path, 'train_pos.txt'), get_degree=True)
    test_edge_data, _ = load_data_from_file(os.path.join(path, 'test_pos.txt'), get_degree=True)

    train_neg_edge_data, _ = load_data_from_file(os.path.join(path1, 'train_neg.txt'), get_degree=False)
    test_neg_edge_data, _ = load_data_from_file(os.path.join(path1, 'test_neg.txt'), get_degree=False)
    
    node_embeddings = load_embeddings(dataset_name, split,emb_dims)
    # laplacian = getL(train_adjacency_mat, len(NODES))
    # spectrum = load_spectrum(dataset_name)
    #print(node_embeddings.shape)
    #exit()
    laplacian = None
    spectrum = None
    #neighbors, neighbors_count = load_neighbors(dataset_name, len(NODES), train_edge_data)
    neighbors, neighbors_count = load_neighbors(dataset_name, max(NODES)+1, train_edge_data)
    #laplacian = get_laplacian(dataset_name)
    
    return (train_edge_data, train_adjacency_mat), (test_edge_data, None), \
            train_neg_edge_data, test_neg_edge_data, node_embeddings, \
            max(NODES)+1, laplacian, spectrum, neighbors, neighbors_count
