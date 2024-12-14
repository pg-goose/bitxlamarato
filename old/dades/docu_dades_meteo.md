## Documentació obtenció de dàdes de la API de MeteoCat

# ApiKey (Header):
X-Api-Key
61AXlft4yD9HZvpBA7yE27xbVm1FkmgA8SZLCuTC

# Check codi Variables
https://api.meteo.cat/xema/v1/variables/mesurades/metadades
Temperatura=32

# Check codi Municipi
https://api.meteo.cat/referencia/v1/municipis
Barcelona=080193
Lleida=251207
Falset=430555
Badalona=080155

# Check estacio referencia Dada/Municipi
https://api.meteo.cat/xema/v1/representatives/metadades/municipis/080193/variables/32
Barcelona(080193)/Temperatura = X4, X8

# Check valor variable(codi) estació(codi) dia(YYYY/MM/DD)
https://api.meteo.cat/xema/v1/variables/mesurades/32/2024/12/14?codiEstacio=X4
Estacio(X4,Barcelona)/Variable(32,temperatura),Dia(2024/12/14)
Resultat:
Temperatura cada 30 min
{
    "data": "2024-12-14T00:00Z",
    "valor": 10.9,
    "estat": " ",
    "baseHoraria": "SH"
}


# Check temperatura mitjana dies d'un mes a una estació(codi):
https://api.meteo.cat/xema/v1/variables/estadistics/diaris/1000?codiEstacio=X8&any=2024&mes=12
Estacio(X4,Barcelona)/Variable(1000,Temperatura Mitjana)/Mes(2024/12)
Resultat:
Per cada dia(XX)
{
    "data": "2024-12-XXZ",
    "valor": 11.6,
    "percentatge": 100
}