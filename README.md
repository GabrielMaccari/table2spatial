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

**Obs:** Apenas colunas com dados exclusivamente numéricos dentro do intervalo esperado para cada coordenada aparecerão como opções para X e Y nessa interface. Os intervalos aceitos para cada coordenada são definidos pela área de uso do SRC selecionado (veja em [EPSG.io](https://www.epsg.io)). 

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
É possível reprojetar uma tabela de pontos usando o table2spatial. Para isso, depois de ter importado sua tabela, clique no botão <img src="https://github.com/FrostPredator/table2spatial/assets/114439033/1ad5a27e-d09b-4909-8e93-7083ea55cdf4" width="20">, na barra de ferramentas do programa. Uma nova aba aparecerá, mostrando o SRC atual do arquivo e uma caixa de seleção para escolha do novo SRC. Você pode digitar os primeiros caracteres do nome de um SRC nessa caixa para encontrá-lo mais facilmente. Clique em OK após selecionar o SRC para reprojetar.

Você também pode marcar a caixa "Salvar coordenadas como colunas na tabela" para que o programa salve as coordenadas reprojetadas em colunas na tabela. Depois de marcar a caixa, insira nos campos X, Y (e Z, no caso de SRCs 3D) os nomes desejados para cada coluna.

<img src="https://github.com/user-attachments/assets/ea124221-3328-4048-a734-71febcc32332" width="300">

**Obs:** Caso você insira um nome de coluna que já existe na tabela, os dados da coluna em questão serão substituídos pelas novas coordenadas.

### 4. Exportando um Arquivo Vetorial
Você pode exportar a tabela como um arquivo vetorial de pontos, em formato GeoPackage, GeoJSON ou Shapefile. Para isso, clique no botão <img src="https://github.com/user-attachments/assets/ceb20ff4-f859-4f3f-8c2a-2ac02db60779" width="20">, na barra de ferramentas. Uma caixa de diálogo aparecerá para escolher o formato de saída e salvar o arquivo. Caso o formato de saída seja GeoPackage, uma outra janela aparecerá em seguida para definir o nome da camada.

**Observações:**
- Você pode salvar múltiplas camadas dentro de um mesmo arquivo GeoPackage. Basta selecionar o mesmo arquivo ao exportar e então especificar um nome diferente para a nova camada a ser inserida. **Caso você defina um nome de camada que já existe dentro do arquivo, ela será substituída**.
- Caso exporte o arquivo como GeoJSON, não há garantia de que seu programa de SIG (QGIS, ArcGIS, etc.) importará o arquivo com os tipos de dados que você especificou para cada coluna/atributo, pois esses tipos de dados não ficam definidos dentro do arquivo.
- Ao exportar como Shapefile, todos os nomes de colunas/atributos serão cortados para um limite de 10 caracteres que é estabelecido pelo formato Shapefile.
- O formato Shapefile não suporta campos de data e hora (Datetime). Logo, ocorrerá um erro ao tentar exportar para Shapefile uma tabela de pontos com uma coluna Datetime. Para resolver, exporte para outro formato ou converta a coluna de data e hora para String.

### 5. Criando Estereogramas e Diagramas de Roseta simples

#### 5.1. Estereogramas

Clique no botão <img src="https://github.com/user-attachments/assets/90457e8d-f5a0-413b-a097-657e4a1bcd30" width="20"> na barra de ferramentas e selecione a opção "Estereograma". Uma janela de configurações aparecerá. Na caixa de seleção de Tipo de medida, escolha o tipo de estrutura a ser representada (planos, linhas ou linhas contidas em planos) e os tipos de ângulo a serem usados.

> **Dip direction:** Sentido de mergulho do plano (0 - 360°). Representa o azimute para onde o plano está mergulhando. Está sempre a 90° do *strike*.
> 
> **Strike:** Direção do plano (0-360°). Corresponde ao azimute da linha de intersecção entre o plano e a superfície horizontal. **Para que o *strike* seja usado no table2spatial, é necessário que seja utilizada a regra da mão direita** para definir qual o ângulo a ser utilizado (o *strike* deve ser sempre igual ao *dip direction* - 90°).
> 
> **Dip:** Ângulo de mergulho vertical do plano (0 - 90°).
> 
> **Plunge:** Ângulo de mergulho vertical da linha (0 - 90°).
> 
> **Trend:** Sentido de mergulho da linha (0 - 360°). Representa o azimute para onde a linha está mergulhando.
> 
> **Rake:** Ângulo entre a linha e o *strike* (considerando-se a regra da mão direita) do plano onde ela está contida, medido no plano (0 - 180°).

Depois de escolher o tipo de medida, selecione as colunas da tabela que contêm cada uma das medidas em questão.

<img src="https://github.com/user-attachments/assets/58d83439-4a36-403e-8898-46f2b25c6bcb" width="250">

Marque a caixa "Plotar planos como pólos" caso queira representar os planos apenas com seus polos. Do contrário, planos são representados por padrão com grandes círculos.

Clique em OK para criar o estereograma, que aparecerá em uma nova janela.

<img src="https://github.com/user-attachments/assets/d1ea14bc-7690-4fb7-a145-5776b322bedd" width="250">

Caso queira salvar o estereograma gerado, clique no botão <img src="https://github.com/user-attachments/assets/e7637387-19a1-4e2e-898d-01d1b8a41e01" width="20">.

#### 5.2. Diagramas de Roseta

Clique no botão <img src="https://github.com/user-attachments/assets/90457e8d-f5a0-413b-a097-657e4a1bcd30" width="20"> na barra de ferramentas e selecione a opção "Diagrama de roseta". Uma janela de configurações aparecerá. Selecione a coluna que contém os azimutes a serem representados (0 - 360°) e o número de direções do diagrama. 

Ao selecionar 16 direções, por exemplo, os azimutes serão particionados em 16 conjuntos de 22,5° (360 / 16), que correspondem às direções cardeais, colaterais e subcolaterais. O primeiro conjunto incluirá azimutes entre 348,75° (norte - 22,5 / 2) e 11,25° (norte + 22,5 / 2), e assim por diante.

**Obs:** Usando o table2spatial, só é possível gerar diagramas de roseta de uma única variável.

Clique em OK para gerar o diagrama, que aparecerá em um nova janela.

Caso queira salvar o estereograma gerado, clique no botão <img src="https://github.com/user-attachments/assets/e7637387-19a1-4e2e-898d-01d1b8a41e01" width="20">.

## Atribuições
Icons by [icons8](https://icons8.com/)
