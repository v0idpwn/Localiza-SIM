#Localiza SIM

Software cuja intencao e possibilitar a localizacao de Onibus em tempo real. Desenvolvido para o Hackathon da i9.

### Conta com:

+ Pagina de visualizacao de rotas
+ Pagina de administrador com possibilidade de adicionar rotas, paradas, horarios e trajetorias customizadas
+ Possibilidade de ver a movimentacao do onibus em tempo real no mapa
+ Modularidade: recebe os dados da movimentacao do onibus via internet, nao restringindo a forma como os dados sao enviados (testado apenas enviando via Android)
+ Possibilidade de uso de dados: todos os dados recebidos sobre a movimentacao dos onibus sao registrados, possibilitando analise posterior.
+ Responsividade: funciona em qualquer tamanho de tela


### Requisitos: 

1. Python 2.7.x
2. Libraries Flask e geojson

### Como executar:

Basta clonar o repositorio, abri-lo e:

```$ export FLASK_APP=localizasim.py```


```$ flask run```



