# llibreries

#install.packages("httr")
#install.packages("jsonlite")

library(httr)
library(jsonlite)
library(tidyr)
library(magrittr)



# https://analisi.transparenciacatalunya.cat/Medi-Ambient/Qualitat-de-l-aire-als-punts-de-mesurament-manuals/qg74-87s9/about_data


#-------------------------------------------------------#



# Carregar llibreries necessàries
library(httr)
library(jsonlite)
library(dplyr)  # Per utilitzar bind_rows

# Definir la URL base de l'API
base_url <- "https://analisi.transparenciacatalunya.cat/resource/qg74-87s9.json?"

# Definir el límit per consulta
limit <- 1000

# Inicialitzar una llista per emmagatzemar totes les dades
resultats <- list()

# Bucle per descarregar les dades en fragments
offset <- 0
continue <- TRUE

while (continue) {
  # Crear la URL amb el limit i l'offset
  url <- paste0(base_url, "$limit=", limit, "&$offset=", offset)
  
  # Fer la consulta a l'API
  resposta <- GET(url)
  
  # Comprovar si la resposta és correcta
  if (status_code(resposta) == 200) {
    # Convertir la resposta JSON en un dataframe
    dades <- fromJSON(content(resposta, "text", encoding = "UTF-8"))
    
    # Afegir les dades a la llista de resultats
    resultats[[length(resultats) + 1]] <- dades
    
    # Actualitzar l'offset per a la propera consulta
    offset <- offset + limit
    
    # Si el nombre de línies obtingudes és menor que el límit, vol dir que hem arribat al final
    if (nrow(dades) < limit) {
      continue <- FALSE
    }
  } else {
    # Si hi ha un error, aturar el bucle
    stop("Error en la consulta API")
  }
}

# Utilitzar bind_rows per combinar tots els dataframes de resultats
dades <- bind_rows(lapply(resultats, as.data.frame))



# Especificar la ruta corregida utilitzant barres inclinades ("/") i fent servir encoding UTF-8
write.csv2(
  dades, 
  file = "MODIFICAR PER LA TEVA CARPETA Dades Obertes/Qualitat_Aire_Manuals.csv", 
  row.names = FALSE, 
  fileEncoding = "UTF-8"
)






#-------------------------------------------------------#


dades$ano %<>% as.numeric()
dades$mes %<>% as.numeric()

max(dades$ano)
max(dades$mes)




dades <- filter(dades,
                nom_estacio %in% c("Badalona (Assemblea de Catalunya)",
                                   "Barcelona (el Poblenou)",
                                   "Lleida (Irurita - Pius XII)",
                                   "Girona (Escola de Música)",
                                   "Tarragona (Universitat Laboral)"))


# Transformar les columnes 'd01' a 'd31' en format llarg

dades_long <- dades %>%
  pivot_longer(cols = starts_with("d"), 
               names_to = "dia", 
               values_to = "valor", 
               names_prefix = "d") %>%
  mutate(dia = as.numeric(dia),  # Convertir el nom del dia en número
         data = as.Date(paste(ano, mes, dia, sep = "-"), "%Y-%m-%d"))  # Crear una columna amb la data completa

# Mostra les primeres files del nou dataframe
dades_long %<>% data.frame()

                              



#GRAFIC ####



library(dplyr)
library(ggplot2)
library(scales)



# Assegurar que la columna 'data' està en format correcte (POSIXct)
dades_long$data <- as.POSIXct(dades_long$data, format = "%Y-%m-%d")

# Filtrar l'any 2024
dades_long <- dades_long %>% filter(ano %in% c(2023:2024))
#dades_long <- dades_long %>% filter(mes > 2)
dades_long$valor %<>% as.numeric()


# Eliminar les files amb NA a la columna 'valor'
dades_long <- dades_long %>% filter(!is.na(valor))

# Crear la columna 'month' si no existeix
dades_long$month <- format(dades_long$data, "%Y-%m")

# Filtrar per PM10


dades_pm10 <- dades_long %>% filter(nom_contaminant == "PM10")



dades_pm10 %<>% select(nom_estacio,
                       nom_contaminant,
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
    subtitle = "Qualitat de l’aire als punts de mesurament manuals",
    x = "",
    y = "Concentració de PM10 (µg/m³)"
  )

# Mostrar el gràfic
print(pp)



# Substituir el punt per una coma a les variables 'latitud' i 'longitud'
# Assegurar-se que latitud i longitud són números i tenen punts com a separador decimal
dades_pm10$latitud <- as.numeric(dades_pm10$latitud)
dades_pm10$longitud <- as.numeric(dades_pm10$longitud)





write.csv2(dades_pm10,("Out_QualitatAIRE_Manual/DadesMeteoCat_PM10.csv"), row.names = F)
ggsave("Out_QualitatAIRE_Manual/GraficsPM10.jpg", plot = pp, width = 40, height = 7, dpi = 300)
ggsave(
  filename = "MODIFICAR PER LA TEVA CARPETA/Dades Obertes/GraficsPM10_Manuals.jpg", 
  plot = pp, 
  width = 15, 
  height = 7, 
  dpi = 300, 
  limitsize = FALSE
)










