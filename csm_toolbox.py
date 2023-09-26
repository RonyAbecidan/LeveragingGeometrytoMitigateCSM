from utils import *
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def harmonic_sum(n):
    i = 1
    s = 0.0
    for i in range(1, n+1):
        s = s + 1/i;
    return s;


class CSM:
      'This class provide methods useful to derive interesting information from a PE matrix'
      def __init__(self,csm_matrix,seed=0):
            '''
            Inputs : 
            @csm_matrix : The matrix M s.t. M[i,j] is the probability of error obtained training on i and evaluating on j.

            Attributes derived:
            @regret_matrix : Derived from csm_matrix. It's the matrix M s.t. M[i,j]=Regret_{i,j} (defined in the paper)
            
            '''
            self.csm_matrix=csm_matrix
            self.N=len(csm_matrix)
            self.regret_matrix=csm_matrix-np.tile(np.diag(csm_matrix).reshape(-1,1),(self.N)).T
            self.seed=seed
            
    
      def greedy_covering(self,epsilon=10):
          '''
          This is the clustering algorithm used for our experiments in the paper.

          Input:
          @epsilon : maximum regret accepted between a representative and the members of its cluster.

          Output :
          @greedy_covering : The covering obtained with the details in the shape of a dictionary where the keys are the clusters
          representatives and the values the sources they are covering.
          @representatives : The list of the representatives (linked to a number)
          @labels : The labels of each source enabling to assign to each source a cluster
        
          Aim:
          This method builds a clustering of the sources involved in the csm matrix.
          The core idea is to see the clustering problem as a set-covering problem and deduce a solution of this problem
          using a greedy algorithm. More details about this idea are given in the article.

          The pseudo-code is available in the article.

          '''  

          P={}
          greedy_covering={}
          not_already_included_in_the_greedy_covering=0
          size=[]

          for i in range(len(self.regret_matrix)):
            P[i]=np.where(self.regret_matrix[i]<epsilon)[0]
            P_size=len(P[i])
            size.append(P_size)
            not_already_included_in_the_greedy_covering+=P_size
       
          while not_already_included_in_the_greedy_covering>0:
              not_already_included_in_the_greedy_covering=0
              points_covered_by_unit_cost={} 

              for i in range(len(self.regret_matrix)):

                if len(P[i]):
                    points_covered_by_unit_cost[i]=len(P[i]) #/constant_cost

                else:
                    points_covered_by_unit_cost[i]=-100

              # we look for the representative covering the maximum number of sources (regret radius < epsilon) 
              k=np.argmax(list(points_covered_by_unit_cost.values()))
              greedy_covering[k]=np.array(list(set(P[k]).union({k}))) 
              #Note : Above, the representative is explicitly included in its own cluster to prevent that the algorithm
              #returns a covering where a representative is covered by an other representative.

              for i in range(len(self.regret_matrix)):
                  #all the sources already covered are deleted from the initial covering
                  P[i]=np.array(list(set(P[i])-set(greedy_covering[k]))) 
                  not_already_included_in_the_greedy_covering+=len(P[i])

          #Safe check : What is the maximum value of the maximum regrets between each representative and its members ? 
          #It should be lower than epsilon
          max_regrets=[]
          for cover in greedy_covering.keys():
              max_regrets.append(self.regret_matrix[cover,greedy_covering[cover]].max())

          print('Max max regrets : ', round(np.max(max_regrets),2))

          #The greedy algorithm used here has a theoretical guarantee giving us an idea about how far we are from an optimal covering
          print('Minimum number of sources for the optimal covering :', np.ceil(len(greedy_covering.keys())/harmonic_sum(max(size))))

          labels_assignement=np.zeros(len(self.regret_matrix))
          
          for j in greedy_covering.keys():
              for value in greedy_covering[j]:
                    labels_assignement[value]=j

    
          return greedy_covering,np.sort(np.unique(labels_assignement)),np.array(labels_assignement)
          
                
      def save_matrix(self,order=None,matrix_type='regret',title=None):
          '''
          This method enables to save an heatmap representing the PE or Regret matrix reordered according to an order
          proposed by the user. By default the order is the identity.

          Inputs : 
          @order : An ordering of the sources in self.csm_matrix 
          @matrix_type : The kind of matrix you want to plot (by default it's the regret matrix)
          @title : The title of the plot you are going to create
          
          '''

          if order is None:
            order=np.arange(0,len(self.csm_matrix))

          if title is None:
            title=f'{matrix_type}_matrix'

          order = np.arange(0,len(self.csm_matrix)) if order is None else order
          reordered_matrix=self.regret_matrix[order,:][:,order] if (matrix_type.lower()=='regret') else self.csm_matrix[order,:][:,order]

          num_ticks = len(reordered_matrix)

          # the index of the position of yticks
          yticks = np.linspace(0, num_ticks - 1, num_ticks,dtype=int)
          # the content of labels of these yticks
          yticklabels = [order[idx] for idx in yticks]

          plt.figure(figsize=(num_ticks,num_ticks))
          sns.heatmap(reordered_matrix, annot=True,cmap="flare",vmin=reordered_matrix.min(),vmax=reordered_matrix.max(),
          yticklabels=yticklabels,xticklabels=yticklabels)

          
          plt.savefig(f'{title}.pdf')
          plt.close()
        
        
        
