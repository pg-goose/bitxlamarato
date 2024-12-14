# llibreries

#install.packages("httr")
#install.packages("jsonlite")

library(httr)
library(jsonlite)
library(tidyr)
library(magrittr)
library(lubridate)
library(dplyr)
library(ggplot2)
library(scales)

# https://analisi.transparenciacatalunya.cat/Medi-Ambient/Qualitat-de-l-aire-als-punts-de-mesurament-autom-t/tasf-thgu/about_data

# Descarregar les dades
url <- "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"
response <- GET(url)

# Convertir les dades JSON a un dataframe
dades <- fromJSON(content(response, "text", encoding = "UTF-8"))

dim(dades)





# Carregar les llibreries necessàries
library(httr)
library(jsonlite)
library(tidyr)
library(magrittr)
library(lubridate)
library(dplyr)
library(ggplot2)
library(scales)

# URL base de l'API

# URL base de l'API
base_url <- "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"

# Definir el límit per consulta
limit <- 1000

# Definir la data de tall (des del 2020)
data_inici <- "2024-01-01"

# Inicialitzar una llista per emmagatzemar totes les dades
resultats <- list()

# Inicialitzar el paràmetre d'offset i variable de control
offset <- 0
continue <- TRUE

# Bucle per descarregar les dades en fragments
while (continue) {
  # Forçar l'offset a un format numèric (evitar notació científica)
  offset_str <- format(offset, scientific = FALSE)
  
  # Crear la consulta amb el filtre de data i l'offset
  resposta <- GET(base_url, query = list(`$limit` = limit,
                                         `$offset` = offset_str,
                                         `$where` = paste0("data >= '", data_inici, "'")))  # Filtrar per data >= 2020-01-01
  
  # Comprovar si la resposta és correcta
  if (status_code(resposta) == 200) {
    # Convertir la resposta JSON en un dataframe
    dades <- fromJSON(content(resposta, "text", encoding = "UTF-8"))
    
    # Verificar si hi ha dades
    if (length(dades) == 0) {
      cat("No hi ha més dades disponibles.\n")
      break
    }
    
    # Afegir les dades a la llista de resultats
    resultats[[length(resultats) + 1]] <- dades
    
    # Actualitzar l'offset per a la propera consulta
    offset <- offset + limit
    
    # Si el nombre de línies obtingudes és menor que el límit, hem arribat al final
    if (nrow(dades) < limit) {
      continue <- FALSE
    }
  } else {
    # Imprimir el codi de resposta per depurar
    print(content(resposta, "text"))
    stop("Error en la consulta API")
  }
}

# Combinar tots els fragments de dades en un únic dataframe
dades <- bind_rows(lapply(resultats, as.data.frame))



# Dades pel Andreu ####


# Especificar la ruta corregida utilitzant barres inclinades ("/") i fent servir encoding UTF-8
write.csv2(
  dades, 
  file = "MODIFICAR PER LA TEVA CARPETA/Dades Obertes/Qualitat_Aire_Automatic.csv", 
  row.names = FALSE, 
  fileEncoding = "UTF-8"
)



#----------#








dades$data <- as.Date(substr(dades$data, 1, 10))

dades$ano <- year(dades$data)
dades$mes <- month(dades$data)

max(dades$ano)
max(dades$mes)




dades <- filter(dades,
                nom_estacio %in% c("Badalona",
                                   "Barcelona (Ciutadella)",
                                   "Barcelona (Gràcia - Sant Gervasi)",
                                   "Barcelona (Poblenou)",
                                   "Girona (Escola de Música)",
                                   "Tarragona (Parc de la Ciutat)",
                                   "Manresa",
                                   "Lleida",
                                   "Vic"))


# Transformar les columnes 'd01' a 'd31' en format llarg

dades_long <- dades %>%
  pivot_longer(cols = starts_with("h"), 
               names_to = "dia", 
               values_to = "valor", 
               names_prefix = "h") %>%
  mutate(dia = as.numeric(dia),  # Convertir el nom del dia en número
         data = as.Date(paste(ano, mes, dia, sep = "-"), "%Y-%m-%d"))  # Crear una columna amb la data completa

# Mostra les primeres files del nou dataframe
dades_long %<>% data.frame()





#GRAFIC ####





# Assegurar que la columna 'data' està en format correcte (POSIXct)
dades_long$data <- as.POSIXct(dades_long$data, format = "%Y-%m-%d")

# Filtrar l'any 2024
dades_long <- dades_long %>% filter(ano == 2024)
dades_long <- dades_long %>% filter(mes > 2)
dades_long$valor %<>% as.numeric()


# Eliminar les files amb NA a la columna 'valor'
dades_long <- dades_long %>% filter(!is.na(valor))

# Crear la columna 'month' si no existeix
dades_long$month <- format(dades_long$data, "%Y-%m")

# Filtrar per PM10


dades_pm10 <- dades_long %>% filter(contaminant == "PM10")



dades_pm10 %<>% select(nom_estacio,
                       contaminant,
                       valor,
                       month,
                       data,
                       longitud,
                       latitud)



# Agrupar per 'month' i 'nom_estacio', i calcular els valors màxims i mínims
summary_data <- dades_pm10 %>%
  group_by(month, nom_estacio) %>%
  summarize(
    max_pm10 = max(valor, na.rm = TRUE),
    min_pm10 = min(valor, na.rm = TRUE),
    .groups = 'drop'
  )

# Unir els màxims i mínims amb les dades originals per obtenir els timestamps corresponents
max_data <- dades_pm10 %>%
  inner_join(summary_data, by = c("nom_estacio", "month")) %>%
  filter(valor == max_pm10)

min_data <- dades_pm10 %>%
  inner_join(summary_data, by = c("nom_estacio", "month")) %>%
  filter(valor == min_pm10)

# Crear el gràfic
pp <- ggplot(dades_pm10, aes(x = data, y = valor, color = nom_estacio, group = nom_estacio)) +
  geom_line() +
  geom_point(data = max_data, aes(x = data, y = max_pm10, color = nom_estacio), size = 3, shape = 18) +
  geom_point(data = min_data, aes(x = data, y = min_pm10, color = nom_estacio), size = 3, shape = 18) +
  scale_x_datetime(labels = date_format("%d %b %y"), breaks = date_breaks("1 month")) +
  scale_color_brewer(palette = "Set1") +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 10),
    legend.position = "bottom",
    legend.title = element_blank()
  ) +
  labs(
    title = "Valors Màxims i Mínims de PM10 per Estació i Mes",
    subtitle = "Qualitat de l’aire als punts de mesurament automatics",
    x = "",
    y = "Concentració de PM10 (µg/m³)"
  )

# Mostrar el gràfic
print(pp)



# Substituir el punt per una coma a les variables 'latitud' i 'longitud'
# Assegurar-se que latitud i longitud són números i tenen punts com a separador decimal
dades_pm10$latitud <- as.numeric(dades_pm10$latitud)
dades_pm10$longitud <- as.numeric(dades_pm10$longitud)



write.csv2(dades_pm10,("Out_QualitatAIRE_Automatic/DadesMeteoCat_PM10_Automatic.csv"), row.names = F)
ggsave("Out_QualitatAIRE_Automatic/GraficsPM10_Automatic.jpg", plot = pp, width = 15, height = 7, dpi = 300)
ggsave(
  filename = "MODIFICAR PER LA TEVA CARPETA/Dades Obertes/GraficsPM10_Automatic.jpg", 
  plot = pp, 
  width = 15, 
  height = 7, 
  dpi = 300, 
  limitsize = FALSE
)









