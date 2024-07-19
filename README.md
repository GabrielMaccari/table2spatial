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

**Obs:** Apenas colunas com dados exclusivamente numéricos dentro do intervalo esperado para cada coordenada aparecerão como opções para X e Y nessa interface. Os intervalos aceitos para cada coordenada são conforme abaixo.

- **Latitude:** -90 a 90°
- **Longitude:** -180 a 180°
- **Northing e Easting:** Área de uso do SRC selecionado (veja em [EPSG.io](https://www.epsg.io)). 

As colunas da tabela então aparecerão em uma lista na interface do table2spatial. Você pode converter os tipos de dados de cada coluna a partir dessa interface, selecionando-os nas caixas de opções à direita do nome da coluna, e também pode excluir e renomear colunas clicando com o botão direito sobre elas.

<img src="https://github.com/FrostPredator/table2spatial/assets/114439033/ace5366a-0d40-4ae9-b964-5f31295df0f8" width="300">

**Obs:** Uma coluna chamada _geometry_ aparecerá na lista de colunas. Ela contém a geometria dos pontos, isto é, os pares de coordenadas para cada ponto. Quando você reprojeta os pontos entre SRCs no table2spatial, as coordenadas são modificadas internamente nessa coluna.

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
É possível reprojetar uma tabela de pontos usando o table2spatial. Para isso, depois de ter importado sua tabela, clique no botão <img src="https://github.com/FrostPredator/table2spatial/assets/114439033/1ad5a27e-d09b-4909-8e93-7083ea55cdf4" width="20px">, na barra de ferramentas do programa. Uma janela aparecerá, mostrando o SRC atual do arquivo e uma caixa de seleção para escolha do novo SRC. Você pode digitar os primeiros caracteres do nome de um SRC nessa caixa para encontrá-lo mais facilmente. Clique em OK após selecionar o SRC para reprojetar.

<img src="https://github.com/FrostPredator/table2spatial/assets/114439033/6f10bf7e-33fa-481e-8fca-d421cd3ffb59" width="500px">

**Obs:** A reprojeção afeta apenas a geometria interna do arquivo vetorial a ser exportado (que aparece com o nome "geometry" na lista de colunas) e não modifica os dados contidos nas colunas de coordenadas que foram selecionadas ao importar a tabela no table2spatial.

### 4. Exportando um Arquivo Vetorial
Você pode exportar a tabela como um arquivo vetorial de pontos, em formato GeoPackage, GeoJSON ou Shapefile. Para isso, clique no botão <img src="https://github.com/user-attachments/assets/ceb20ff4-f859-4f3f-8c2a-2ac02db60779" width="20px">, na barra de ferramentas. Uma caixa de diálogo aparecerá para escolher o formato de saída e salvar o arquivo. Caso o formato de saída seja GeoPackage, uma outra janela aparecerá em seguida para definir o nome da camada.

**Observações:**
- Você pode salvar múltiplas camadas dentro de um mesmo arquivo GeoPackage. Basta selecionar o mesmo arquivo ao exportar e então especificar um nome diferente para a nova camada a ser inserida. **Caso você defina um nome de camada que já existe dentro do arquivo, ela será substituída**.
- Caso exporte o arquivo como GeoJSON, não há garantia de que seu programa de SIG (QGIS, ArcGIS, etc.) importará o arquivo com os tipos de dados que você especificou para cada coluna/atributo, pois esses tipos de dados não ficam definidos dentro do arquivo.
- Ao exportar como Shapefile, todos os nomes de colunas/atributos serão cortados para um limite de 10 caracteres que é estabelecido pelo formato Shapefile.
- O formato Shapefile não suporta campos de data e hora (Datetime). Logo, ocorrerá um erro ao tentar exportar para Shapefile uma tabela de pontos com uma coluna Datetime. Para resolver, exporte para outro formato ou converta a coluna de data e hora para String.

### 5. Criando Estereogramas e Diagramas de Roseta
Em breve...

## Atribuições
Icons by [icons8](https://icons8.com/)
