# table2spatial
Aplicativo desenvolvido em Python para conversão de tabelas de pontos georreferenciados em camadas vetoriais nos formatos GeoPackage, Shapefile e GeoJSON.

Dicas de utilização:
-Organize as coordenadas dos pontos em 2 colunas distintas (Ex: latitude e longitude);
-Os formatos suportados para coordenadas são graus decimais (Ex: -27,096214) e UTM (Ex: 6989596). Graus, minutos e segundos (GMS) não é um formato suportado.
-O separador decimal considerado na leitura de arquivos CSV é o ponto.
-Várias abas de um mesmo arquivo XLSX ou ODS podem ser mescladas usando um campo de identificação em comum para os pontos;
-Caso deseje converter os dados para Shapefile, certifique-se de que os nomes das colunas da tabela não possuem espaços e caracteres especiais, e que eles não ultrapassam 10 caracteres (Ex: cod_ponto).
-Para exportar múltiplas camadas dentro de um mesmo GeoPackage, simplesmente selecione o mesmo arquivo .gpkg ao salvar e insira um nome diferente para a nova camada.
