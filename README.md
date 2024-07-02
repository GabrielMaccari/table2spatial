<div align="center"/>
  <p>
    <h1>table2spatial</h1>
      <p>
        Aplicativo para conversão de tabelas de pontos georreferenciados em camadas vetoriais para uso em Sistemas de Informações Geográficas.
      </p>
      <a href="https://github.com/FrostPredator/table2spatial/releases/latest"><img alt="Static Badge" src="https://img.shields.io/badge/Download%20-%20Vers%C3%A3o%20mais%20recente%20-%20%231082c3"></a>
      <img alt="Static Badge" src="https://img.shields.io/github/downloads/FrostPredator/table2spatial/total">
      <br>
      <br>
      <img src="https://github.com/FrostPredator/table2spatial/assets/114439033/b4501243-54e0-44bf-bea9-3945660ce4c8">
  <p>
</div>

## Features
- Importa tabelas de pontos nos formatos XLSX, CSV, ODT e XLSM
- Lê coordenadas em graus decimais, UTM e GMS (GG°MM'SS,ssss"D)
- Mescla planilhas de um mesmo arquivo usando uma coluna identificadora
- Converte dados das colunas entre diferentes tipos de dados (string, integer, float, boolean e datetime)
- Reprojeta pontos entre diferentes SRCs
- Exporta arquivos vetoriais de pontos nos formatos GeoPackage, GeoJSON e Shapefile para uso em SIG
- Plota estereogramas e diagramas de roseta simples

## Como Utilizar

### 1. Importando uma Tabela de Pontos
Organize seus dados em uma tabela em formato XLSX, XLSM, CSV ou ODT, com cada linha representando um ponto. Separe as coordenadas de cada ponto em duas colunas distintas. Você pode usar coordenadas em formato UTM (Ex: 6989596,00), graus decimais (Ex: -27,19899) ou graus, minutos e segundos (Ex: 27°11′56,3746″S). A tabela abaixo mostra um exemplo de como organizar os dados:

| Cod_ponto | Latitude  | Longitude |    Data    | Afloramento | Amostras |
| --------- | :-------: | :-------: | :--------: | :---------: | :------: |
| EX001     | -27,19899 | -48,79127 | 24/05/2022 |     Sim     |    2     |
| EX002     | -27,19623 | -48,78323 | 24/05/2022 |     Sim     |    0     |
| EX003     | -27,19315 | -48,77848 | 24/05/2022 |     Sim     |    2     |
| EX004     | -27,19588 | -48,76274 | 25/05/2022 |     Não     |    0     |

Com os dados devidamente organizados, clique no botão <img src="https://github.com/FrostPredator/table2spatial/assets/114439033/1ad6f7b4-f95a-4ad0-bad5-ef648e87263d" width="20"> na barra de ferramentas do table2spatial e selecione o arquivo da tabela. Na interface de configuração (imagem abaixo), selecione a planilha do arquivo que contém as coordenadas dos pontos, o sistema de referências (SRC) das coordenadas e também as colunas onde as coordenadas de cada eixo se encontram. Clique no botão OK para importar os dados.

<img src="https://github.com/FrostPredator/table2spatial/assets/114439033/818413b5-7ecd-47bf-ba85-0805d256501e" width="300">

As colunas da tabela então aparecerão em uma lista na interface do table2spatial. Você pode converter os tipos de dados de cada coluna a partir dessa interface, selecionando-os nas caixas de opções à direita do nome da coluna, e também pode excluir e renomear colunas clicando com o botão direito sobre elas.

<img src="https://github.com/FrostPredator/table2spatial/assets/114439033/ace5366a-0d40-4ae9-b964-5f31295df0f8" width="300">

### 2. Mesclando Planilhas de um Arquivo
Você pode mesclar múltiplas planilhas (abas) de um mesmo arquivo, desde que haja uma coluna identificadora em comum entre elas. Para realizar a mesclagem de planilhas, clique no botão <img src="https://github.com/FrostPredator/table2spatial/assets/114439033/5084056c-4e26-41e7-9c90-7de734b0ed49" width="20">, na barra de ferramentas, e então selecione a coluna identificadora. As planilhas serão mescladas com base na coluna selecionada, e um aviso será exibido, relatando o sucesso.

No exemplo abaixo, a coluna **Cod_ponto** é usada para interligar as linhas das duas planilhas mescladas.

**PLANILHA 1:**

| Cod_ponto | Latitude  | Longitude |    Data    | Afloramento | Amostras |
| --------- | :-------: | :-------: | :--------: | :---------: | :------: |
| EX001     | -27,19899 | -48,79127 | 24/05/2022 |     Sim     |    2     |
| EX002     | -27,19623 | -48,78323 | 24/05/2022 |     Sim     |    0     |
| EX003     | -27,19315 | -48,77848 | 24/05/2022 |     Sim     |    2     |
| EX004     | -27,19588 | -48,76274 | 25/05/2022 |     Não     |    0     |

**PLANILHA 2:**

| Cod_ponto | Sentido_foliacao | Mergulho_foliacao |
|-----------|:----------------:|:-----------------:|
| EX001     |        240       |         30        |
| EX002     |        240       |         40        |
| EX003     |        220       |         35        |
| EX004     |                  |                   |

**PLANILHA MESCLADA:**

| Cod_ponto | Latitude  | Longitude |    Data    | Afloramento | Amostras | Sentido_foliacao | Mergulho_foliacao |
| --------- | :-------: | :-------: | :--------: | :---------: | :------: |:----------------:|:-----------------:|
| EX001     | -27,19899 | -48,79127 | 24/05/2022 |     Sim     |    2     |        240       |         30        |
| EX002     | -27,19623 | -48,78323 | 24/05/2022 |     Sim     |    0     |        220       |         35        |
| EX003     | -27,19315 | -48,77848 | 24/05/2022 |     Sim     |    2     |        240       |         40        |
| EX004     | -27,19588 | -48,76274 | 25/05/2022 |     Não     |    0     |                  |                   |

### 3. Reprojetando os Pontos para Outro SRC
Em breve...

### 4. Exportando um Arquivo Vetorial
Em breve...

### 5. Criando Estereogramas e Diagramas de Roseta
Em breve...

## Atribuições
@ 2024 Gabriel Maccari

Icons by [icons8](https://icons8.com/)
