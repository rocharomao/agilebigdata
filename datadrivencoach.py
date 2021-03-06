# -*- coding: utf-8 -*-
"""DataDrivenCoach.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r5CKuvWcmi76igbAZQFtrkW0nxk_O8Vg
"""

#Formulário de interação
#@title Data-Driven Agile Coach { display-mode: "code" }
#Importação de bibliotecas
import seaborn as sns
from pandas import read_csv
import pandas as pd
from google.colab import files
import IPython
from google.colab import output
import io #Biblioteca para importação de arquivo local
#https://github.com/rocharomao/agilebigdata/raw/master/PredTiposTamInput.csv
#https://raw.githubusercontent.com/rocharomao/agilebigdata/master/PredInput.csv

#Nome do arquivo no fomulário
Arquivo = 'Base local' #@param {type:"string"}


#No do arquivo para importação
name = Arquivo
Tipo = "Monte Carlo" #@param ["Base Jira","Visualizar dados", "Box-Plot","Histrograma", "Scatterplot", "Scatterplot colorido", "Linha","Dispersão","Previsibilidade", "Análise do Agile Coach", "Correlação","Monte Carlo", "Probabilidade com Machine Learning", "Clusterizar por tipo", "Resumo dos dados"] {allow-input: false}

#Solicita certeza de previsibilidade se selecionado Previsibilidade
if Tipo == "Previsibilidade":
  Certeza = int(input("Por favor, informe o % de certeza desejado para a previsão: "))
  #Certeza = 100  #@param {type: "slider", min: 0, max: 100}

if Tipo == "Monte Carlo":
  qtd = int(input("Número de simulações: "))

#Solicita arquivo se selecionada opção Correlação
if Tipo == "Correlação":
  arqCorr = files.upload()



#-----------Função para base montar base local
def montarJira(arqJira):  
  lsKey = []
  lsKey = list(arqJira.keys())
  dfJ = pd.read_csv(io.StringIO(arqJira[lsKey[0]].decode('latin-1')),delimiter=";")
  #Adicionar coluna de Dias
  dfJ['Dias'] = (pd.to_datetime(dfJ['Categoria do status alterada']) - pd.to_datetime(dfJ['Criado'])).astype('timedelta64[ns]').dt.days
  dfJira = dfJ[['Tipo de item', 'Dias']]
  dfJira.columns = ['Type','Dias']
  return dfJira

#Solicita arquivo se selecionada Base Jira
if Tipo == "Base Jira":
  arqJira = ''
  arqJira = files.upload()
  if arqJira == {}:
    print('Faltou selecionar o arquivo!')
  else:
    #Chamar função para tratamento de base local
    data = montarJira(arqJira)
    

#Importação do arquivo
if Arquivo == 'Base local':
  #Chamar função para converter base local
  print('Base local Selecionada!')
else:
  #data = read_csv(name, sep=";")
  data = read_csv(name, delimiter=";", encoding="latin-1")


#Função para definição do grático Box-Plot
def boxplot(data):
  #Apresentação do gráfico Box-Plot
  ax = sns.boxplot(x="Dias", y="Type", data=data)
 
#Função para definição do grático Scatterplot
def scatter(data):
  #Apresentação do gráfico Scatterplot
  data.plot('Dias', 'Type', kind='scatter')
 
 
#Função para definição do grático Scatterplot colorido
def scattercolor(data):
  #Apresentação do gráfico Scatterplot colorido
  ax = sns.catplot(x="Dias", y="Type", data=data)
 
#Função para definição do gráfico Histograma
def barplot(data):
  #Apresentação do histograma
  sns.catplot(x='Dias', kind ='count', 
              data = data, aspect = 2, 
              palette = "GnBu_d")
 
#Função para definição do grático de linha
def lineplot(data):
  #Apresentação do gráfico de linha
  data.plot()
 
#Função para definição do gráfico com desvios padrão
def dpplot(data):
  #Medição de dispersão pelo desvio padrão
  data.groupby(['Type']).std().plot(kind='bar')
 
#Função para apresentar gráfico por quantil
def prevplot(data, q=0.85):
  #Apresentação da quantidade de dias por quantil
  data.groupby(['Type']).quantile(q).plot(kind='bar')
 
#Função para análise do Agile Coach
def agilecoachPedro():
  #Apresenta análise em HTML
  display(IPython.display.HTML('''
      <H1>A duração do tipo Alpha TestS pode variar muito. 
        <br>É interessante rever a classificação dos itens.
      </H1>
      '''))

#Função para análise de correlação
def correlacionar(): #(df1, df2):
  #Apresenta percentual de correlação 
  direcao = 'Positiva (Os dois fatores tendem a crescer juntos)'
  corr = 80
  analise = 'Alta'
  #Apresenta resultado percentual da correlação
  display(IPython.display.HTML('''
      <H2>Correlação: ''' + analise + ''' 
        <br>Direção: ''' + direcao + ''' 
        <br>Percentual de correlação: ''' + str(corr) + '''% 
      </H2>
      '''))
#-------------------------------#-----------------------------------
#Importação de bibliotecas para Monte Carlo
import scipy.stats as stats
import pymc3 as mc
import matplotlib.pyplot as plt
import numpy as np

#Função de elicitação 
def elicit(name, data):
    y = np.sort(data)
    width = y.max()-y.min()
    par = stats.beta.fit(y[1:-1], floc=y.min(), fscale=y.max())
    var = stats.beta(*par)
    
    scaled_mu = var.mean()/width
    scaled_sd = var.std()/width
    scaled = mc.Beta(f"{name}_scaled__", mu=scaled_mu, sd=scaled_sd)
    dist = mc.Deterministic(name, y.min() + (scaled * width))
    dist.var = var
    
    return dist

#Função para sumarizar variárel para o histograma
def sumplot(data):
    sns.distplot(data)
    colors = iter(sns.color_palette())
    
    m = np.mean(data)
    plt.axvline(m, linestyle=":", color=next(colors), label=f"mean = {m:0.2f}")

    ps = [50, 90, 95, 99]
    for p in ps:
        x = np.percentile(data, p)
        plt.axvline(x, linestyle=":", color=next(colors), label=f"{p:0.2f} = {x:0,.2f}")
    plt.legend()

#Função para remoção de duração 0
def removeponta(ls):
  for i in range(ls.count(0)):
    ls.remove(0)
    ls.append(1)
  ls.append(0)
  return ls

#Função para execução da simulação Monte Carlo
def gerarsimulacao(data, qtd=10000):
  #Armazernar serie dias
  dt = data['Dias']
  #Converte para tipo lista
  ls = list(dt)
  #Executa função para remover valor 0
  ls = removeponta(ls)
  #Criação do modelo
  model = mc.Model()

  #Execução do modelo
  with model:
      pl = elicit("Dias", ls)

  sumplot(pl.var.rvs(qtd))

#---------------------------------- Análise do especialista-------------------------
#Classe Coach virtual para análise dos dados
class Coach: 
  def getMaiorDispersao(df):
      dfdesc = montarDescribe(df)
      #Consultar o name do index da primeira linha
      tipo = dfdesc.iloc[0].name
      analise = 'O tipo de entrega '+ tipo + ' é o maior ofensor da previsibilidade do time.'                                  
      return analise

  def getMenorDispersao(df):
      #dfdesc = montarDescribe(df)
      #Consultar o name do index da primeira linha
      tipo = df
      analise = 'O tipo de entrega '+ tipo + ' é o maior ofensor da previsibilidade do time.'                                  
      return analise

  def getListarDispersoes(self,df):
    dfdesc = montarDescribe(df)
    #Consultar o name do index da primeira linha
    dfdesc.iloc[0].name

    analise = 'O tipo de entrega '+ tipo + ' apresentou alta dispersão'                                  
    return analise

  def montarDescribe(df):
  #Calcular média de dias por tipo
    dfdesc = df.groupby(['Type']).mean()
    #Renomear coluna Dias para "mean"
    dfdesc.columns = ['mean']
    #Calcular desvio padrão por tipo
    dfdesc['std'] = df.groupby(['Type']).std()
    #Calcular mediana por tipo e apresentar
    dfdesc['median'] =  df.groupby(['Type']).median()
    #Calcular mínima por tipo e apresentar
    dfdesc['min'] =  df.groupby(['Type']).min()
    #Calcular máxima por tipo e apresentar
    dfdesc['max'] =  df.groupby(['Type']).max()
    #Calcular a quantidade por tipo
    dfdesc['qtd'] = df.groupby(['Type']).count()
    #Calcular coeficiente de variação por tipo e apresentar em percentual com duas casas decimais
    dfdesc['cv'] =  (dfdesc['std'] / dfdesc['mean'])*100
    #Imprimir valores
    dfdesc.sort_values(by='cv',ascending=False)
    #Arredondar valores
    dfdesc = round(dfdesc, 2)
    #Renomear colunas
    dfdesc.columns = ['Média', 'Desvio padrão', 'Mediana', 'Mínimo', 'Máximo','Quantidade', 'Coeficiente de variação %']
    return dfdesc 

#-------------- Classe Clusterizadora ----------------------
#Bibliotecas da Clusterização por tipo
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

#Função para montagem do DataFrame Cluster
def montarDFCluster(df):
  nametipo = 'Type'
  lsTipos = list(df[nametipo].unique())
  lsdfTipos = []
  for item in lsTipos:
    df1 = df.loc[df[nametipo] == item]  
    lsdfTipos.append(df1)
  return lsdfTipos

#Função auxiliar para o caso de apenas uma feature
def addColAux(lsdfTipos, i):
  duracao = 'Dias'
  dfcls =  lsdfTipos[i][['Dias']]
  lstfix = '1'* len(dfcls)
  dfcls['num'] = lstfix[i]
  return dfcls

#Função para apresentar Elbow
def apresetarElbow(df, n):
  #K Means and Elbow
  sse = {}
  for k in range(1, n):
      kmeans = KMeans(n_clusters=k, max_iter=1000).fit(df)
      #data["clusters"] = kmeans.labels_
      #print(data["clusters"])
      sse[k] = kmeans.inertia_ # Inertia: Sum of distances of samples to their closest cluster center
  plt.figure()
  plt.plot(list(sse.keys()), list(sse.values()))
  plt.xlabel("Number of cluster")
  plt.ylabel("SSE")
  plt.show()

def executarKmeans(df,n):
  #Aplicação de KMeans
  modeloKmeans = KMeans(n_clusters=n)
  modeloKmeans.fit(df)
  #Adicionar coluna com o número do cluster
  df["clusters"] = modeloKmeans.labels_
  return df


#Clusterização por tipo
class Clusterizador:
    #Função oquestradora de Cluster
    def clusterizar(df, n = 2, idf = 1):
      lsdfTipos = montarDFCluster(df)
      dfcls = addColAux(lsdfTipos, idf)
      # apresetarElbow(dfcls)
      if (len(dfcls))>=n:
        km = executarKmeans(dfcls,n)
        km['Tamanho'] = km['clusters'].replace([1, 0], ['PP', 'P'])
        kmTam = km[['Dias', 'Tamanho']]
      else:
        kmTam = 'Quantidade de classes maior que o número de elementos. O tamanho máximo possível é: ' + str(len(dfcls))         
      return kmTam

#----------------- Chamadas para clusterização -----------------
if Tipo == "Clusterizar por tipo":
  idTipo = int(input("Informe o Tipo: "))
  classes = int(input("Número de clusters: "))
  cluster = Clusterizador
  dfcls = cluster.clusterizar(data, n = classes, idf = idTipo)
  display(IPython.display.HTML(dfcls.to_html()))


#Classe de definição dos tipos
class Analise:
  box = "Box-Plot";
  hist = "Histrograma";
  sct = "Scatterplot";
  lin = "Linha";
  sctcolor = "Scatterplot colorido";
  std = "Dispersão";
  prev = "Previsibilidade";
  agc = "Análise do Agile Coach";
  corr = "Correlação"
  mc = "Monte Carlo"
  ac = "Resumo dos dados"
  vs = "Visualizar dados"
  ml = "Probabilidade com Machine Learning"

# Recebe o tipo de análise
tipo = Tipo;
 
if tipo == Analise.box:
  boxplot(data);
elif tipo == Analise.hist:
  barplot(data);
elif tipo == Analise.sct:
  scatter(data);
elif tipo == Analise.sctcolor:
  scattercolor(data);
elif tipo == Analise.lin:
  lineplot(data);
elif tipo == Analise.std:
  dpplot(data);
elif tipo == Analise.agc:
  agilecoachPedro();    
elif tipo == Analise.prev:
  prevplot(data, q=Certeza/100)
elif tipo == Analise.corr:
  correlacionar()
elif tipo == Analise.mc:
  gerarsimulacao(data, qtd)
elif tipo == Analise.ac:
  coach = Coach
  analise = coach.montarDescribe(data)
  display(IPython.display.HTML(analise.to_html()))
elif tipo == Analise.ml:
  gerarsimulacao(data, qtd)
elif tipo == Analise.vs:
  display(IPython.display.HTML(data.to_html()))
else:
  print("Selecione um tipo de análise!");