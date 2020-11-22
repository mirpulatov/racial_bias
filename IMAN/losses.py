import torch

def mmd(D_s, D_t):
  D_s_mean = D_s.view(D_s.size(0), -1).mean(0)
  D_t_mean = D_t.view(D_t.size(0), -1).mean(0)
  return (D_s_mean - D_t_mean).pow(2).sum()


def multilayer_mmd(s_adopt_layers_out, t_adopt_layers_out):
  m_mmd = 0
  for D_s, D_t in zip(s_adopt_layers_out, t_adopt_layers_out):
    m_mmd += mmd(D_s, D_t)
  return m_mmd


def mutual_information_loss(probs, gamma):

  H_of_O_under_condition_X = -(probs * torch.log2(probs + 1e-12)).sum() / probs.size(0)

  probs_marginal = probs.mean(dim=0)
  H_of_O = -(probs_marginal * torch.log2(probs_marginal + 1e-12)).sum()
  
  mi_loss = H_of_O_under_condition_X - gamma * H_of_O

  return mi_loss
