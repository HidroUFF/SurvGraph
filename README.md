<p align="center">
  <img src="https://user-images.githubusercontent.com/69862177/92131158-0030af00-eddc-11ea-8bc1-c371b11861c9.png" width="350" alt="Logo SurvGraph">
</p>


# SurvGraph
O SurvGraph é uma aplicação desenvolvida para realizar edições em gráficos. 
O programa possui as seguintes funcionalidades:
* Adicionar ou remover pontos nos gráficos através de interpolação (1º, 2º ou 3º);
* Recortar os gráficos;
* Remover ruidos dos gráficos. (Função útil para gráficos provenientes de atividades experimentais);
* Realizar Transformada Rápida de Fourier (FFT) dos gráficos. 

### Tecnologia 

    Python (vers. 3.8.3)
    Qt Designer

### Execução do SurvGraph

* Basta baixar o SurvGraph.exe em seu computador e executa-lo. Não é necessário fazer qualquer instalação.

   (O arquivo executável é compativel apenas com o sistema operacional Windows)

### Instalação e execução do SurvGraph (Via código)

* Baixe a aplicação com o seguinte comando:
    git clone https://github.com/HidroUFF/SurvGraph.git

* Como o ambiente virtual acompanha o código, não é necessário instalar nenhuma biblioteca

* Certifique-se que o seu compilador está aberto na pasta SurvGraph antes de iniciar o programa.

* O arquivo principal é o SurvGraph.py, então sempre inicie o programa por ele.

* Para abrir e começar a editar um gráfico é necessário ter um arquivo .txt ou .csv com as coordenadas X e Y nessa ordem.
  (No arquivo .txt as coordenadas devem estar organizadas em colunas, sendo as colunas separadas por tabulação)

* Os arquivos que contem as coordenas dos gráficos podem ter cabeçalho.

* O programa entende números com separador decimal tanto usando a vírgula quanto usando o ponto.
  (Ex. 1000,1 ou 1000.1)

* ***Não usar separador de milhar nas coordenadas***

* O arquivo file_buttons.py são as imagens usadas no programa, recomendo não realizar alterações nele.

## Autor e Contato

    Rodrigo Neves
    e-mail: rodrigo_junior@id.uff.br

## Orientador

    Profº Gabriel Nascimento

## Citando o SurvGraph

  Se o SurvGraph contribuiu para algum projeto ou pesquisa que levo a publicação, por favor cite-o.
    https://zenodo.org/badge/291381958.svg


<p align="center">
  <img src="https://user-images.githubusercontent.com/69862177/92263515-21180380-eeb3-11ea-9c9f-d1509b75c6dc.png" width="350" alt="Logo HidroUFF">
  <img src="https://user-images.githubusercontent.com/69862177/92263566-37be5a80-eeb3-11ea-99ea-f2d342988fe0.png"
  width="350" alt="Brasão UFF">
</p>

