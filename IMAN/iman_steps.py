import networkx as nx
import torch
import torch.nn.functional as F
import torchvision.datasets
#from tqdm import tqdm
from tqdm.notebook import tqdm

from losses import multilayer_mmd, mutual_information_loss
from utils import zip_longest



def pretraining_step(s_input, s_labels, t_input, model, optimizer, lambda_):

  _, s_adopt_layers_out, s_scores = model(s_input, calc_scores=True)

  _, t_adopt_layers_out, _ = model(t_input, calc_scores=False)

  s_clf_loss = F.cross_entropy(s_scores, s_labels)

  mmd_loss = multilayer_mmd(s_adopt_layers_out, t_adopt_layers_out)

  loss = s_clf_loss + lambda_ * mmd_loss

  optimizer.zero_grad()
  loss.backward()
  optimizer.step()

  return s_clf_loss.item(), mmd_loss.item()



def pretraining_epoch(model, s_loader, t_loader, optimizer, device, lambda_): 
  model.train()

  s_clf_loss = []
  mmd_loss = []

  for s_batch, t_batch in tqdm(zip_longest(s_loader, t_loader), 
                               total=max(len(s_loader), len(t_loader)),
                               desc="epoch progress"):
    s_input, s_labels = s_batch[0].to(device), s_batch[1].to(device)
    t_input = t_batch[0].to(device)

    s_clf_loss_batch, mmd_loss_batch = pretraining_step(s_input, s_labels, t_input, model,
                                                        optimizer, lambda_)
    s_clf_loss.append(s_clf_loss_batch)
    mmd_loss.append(mmd_loss_batch)

  return s_clf_loss, mmd_loss



def cluster(model, data_loader, device, sim_thresh, min_cluster_size):

  assert isinstance(data_loader.sampler, torch.utils.data.SequentialSampler)
  assert data_loader.drop_last == False

  # calculating domain embeddings
  domain_dataset_embeddings_list = []
  model.eval()
  for batch in tqdm(data_loader, total=len(data_loader), desc="extracting embeddings..."):
    t_input = batch[0].to(device)
    with torch.no_grad():
      batch_embeddings, _, _ = model(t_input, calc_scores=False)
    domain_dataset_embeddings_list.append(batch_embeddings.cpu())
  
  domain_dataset_embeddings = torch.cat(domain_dataset_embeddings_list, dim=0)
  
  # building a clustering graph
  edges = []
  n_nodes = len(data_loader.dataset)

  for node_i in tqdm(range(n_nodes - 1), desc="calculating cosine similarities..."):
    node_i_cos_sims = F.cosine_similarity(domain_dataset_embeddings[node_i: node_i+1], 
                                          domain_dataset_embeddings[node_i+1:])
    neighbours_indexes = (node_i_cos_sims > sim_thresh).nonzero(as_tuple=True)[0].tolist()
    for node in neighbours_indexes:
      node_j = node + node_i + 1
      edges.append((node_i, node_j))

  G = nx.Graph(edges)
  connected_components = list(nx.connected_components(G))
  clusters = [c for c in connected_components if len(c) > min_cluster_size]

  # node -- image index in the dataset, cluster_num -- pseudo-label
  node_to_cluster_num = {node: cluster_num 
                         for cluster_num, cluster in enumerate(clusters) 
                           for node in cluster}
  
  return node_to_cluster_num



def get_data_for_preadaptation(model, target_domain_data_loader, device, 
                               sim_thresh, min_cluster_size):

  dataset = target_domain_data_loader.dataset

  img_idx_to_pseudo_label = cluster(model, target_domain_data_loader, device,
                                    sim_thresh, min_cluster_size)
  
  pseudo_samples = []

  for img_idx, pseudo_label in img_idx_to_pseudo_label.items():
    path = dataset.samples[img_idx][0]
    pseudo_samples.append((path, pseudo_label))

  pseudo_dataset = torchvision.datasets.ImageFolder(dataset.root, 
                                                    transform=dataset.transform)
  pseudo_dataset.samples = pseudo_samples

  pseudo_loader = torch.utils.data.DataLoader(pseudo_dataset, 
                               batch_size=target_domain_data_loader.batch_size,
                               shuffle=True,
                               num_workers=target_domain_data_loader.num_workers, 
                               pin_memory=True, drop_last=True)
  
  return pseudo_loader



def preadaptation_epoch(model, preadaptation_dataloader, target_domain_scoring,
                        optimizer, device):
  model.train()

  losses = []

  for (input, target) in tqdm(preadaptation_dataloader, 
                              total=len(preadaptation_dataloader),
                              desc="epoch progress"):
    input, target = input.to(device), target.to(device)
    embeddings, _, _ = model(input, calc_scores=False)
    scores = target_domain_scoring(embeddings, target)
    loss = F.cross_entropy(scores, target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    losses.append(loss.item())

  return losses



def mi_adaptation_epoch(model, target_domain_scoring, s_loader, t_loader, 
                        optimizer, device, alpha, beta, gamma):
  model.train()

  losses = []
  s_clf_losses, mmd_losses, mi_losses = [], [], []

  for s_batch, t_batch in tqdm(zip_longest(s_loader, t_loader),
                               total=max(len(s_loader), len(t_loader)),
                               desc="epoch progress"):
    s_input, s_labels = s_batch[0].to(device), s_batch[1].to(device)
    t_input, t_labels = t_batch[0].to(device), t_batch[1].to(device)

    _, s_adopt_layers_out, s_scores = model(s_input, calc_scores=True)

    t_embeddings, t_adopt_layers_out, _ = model(t_input, calc_scores=False)
    t_scores = target_domain_scoring(t_embeddings)
    t_probs = F.softmax(t_scores, dim=1)

    mmd_loss = multilayer_mmd(s_adopt_layers_out, t_adopt_layers_out)

    s_clf_loss = F.cross_entropy(s_scores, s_labels)

    mi_loss = mutual_information_loss(t_probs, gamma)

    loss = s_clf_loss + alpha * mmd_loss + beta * mi_loss

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    s_clf_losses.append(s_clf_loss.item())
    mmd_losses.append(mmd_loss.item())
    mi_losses.append(mi_loss.item())
    losses.append(loss.item())

  return losses, s_clf_losses, mmd_losses, mi_losses
