# Estacions Mapa
# https://www.meteo.cat/observacions/xema?dia=2024-05-09T11:30Z


#Api key ####
# 61AXlft4yD9HZvpBA7yE27xbVm1FkmgA8SZLCuTC


# WEB : ####

# https://apidocs.meteocat.gencat.cat/section/referencia-tecnica/ 

# https://emf-creaf.github.io/meteospain/
# 



# Llista de paquets necessaris
paquets <- c("magrittr", "meteospain", "dplyr", "ggplot2", "ggforce", "units", "sf", "keyring")

# Comprova si els paquets estan instal·lats, sinó els instal·la
for (paquet in paquets) {
  if (!require(paquet, character.only = TRUE)) {
    install.packages(paquet, dependencies = TRUE)
    library(paquet, character.only = TRUE)
  }
}

# Carrega els paquets
library(magrittr)
library(meteospain)
library(dplyr)
library(ggplot2)
library(ggforce)
library(units)
library(sf)
library(keyring)

library(magrittr)
library(meteospain)
library(dplyr)
library(ggplot2)
library(ggforce)
library(units)
library(sf)
library(keyring)
library(lubridate)

key_set('meteocat',
        prompt = "Password Marcos:")








##############



# Funció per recopilar les dades meteorològiques de Catalunya mensualment
recopilar_dades_meteo <- function() {
  # Inicialitzar el data frame que acumularà les dades
  cat <- tibble()
  
  # Obtenir l'any i mes actual
  any_actual <- year(Sys.Date())
  mes_actual <- month(Sys.Date())
  
  # Bucle des de gener fins al mes actual
  for (mes in 1:mes_actual) {
    start_date <- as.Date(paste(any_actual, mes, "01", sep = "-"))
    
    # Configurar opcions de l'API
    api_options <- meteocat_options(
      resolution = 'daily',
      start_date = start_date,
      api_key = key_get('meteocat')
    )
    
    # Recuperar les dades meteorològiques per aquest mes
    catalunya <- tryCatch({
      get_meteo_from('meteocat', options = api_options)
    }, error = function(e) {
      message("Error en recuperar les dades: ", e$message)
      return(tibble())  # Retorna un tibble buit en cas d'error
    })
    
    # Combina les dades noves amb les existents si no està buit
    if (nrow(catalunya) > 0) {
      if (ncol(cat) == 0) {
        cat <- catalunya  # Si cat encara no té columnes, assigna directament
      } else {
        cat <- bind_rows(cat, catalunya)  # Altrament, combina les files
      }
    }
  }
  
  # Retorna el data frame complet
  return(cat)
}

# Executar la funció i imprimir resultats
cat_data <- recopilar_dades_meteo()


cat_data %<>% filter(station_name %in% c("Lleida - la Femosa",
                                         "Badalona - Museu",
                                         "Falset",
                                         "Barcelona - Observatori Fabra",
                                         "Palafrugell"))


cat_data$service <- NULL


cat_data$CodiEscola[cat_data$station_name == "Lleida - la Femosa"] <- "1"
cat_data$CodiEscola[cat_data$station_name == "Badalona - Museu"] <- "2"
cat_data$CodiEscola[cat_data$station_name == "Falset"] <- "3"
cat_data$CodiEscola[cat_data$station_name == "Barcelona - Observatori Fabra"] <- "4"
cat_data$CodiEscola[cat_data$station_name == "Palafrugell"] <- "5"


table(cat_data$CodiEscola, useNA = "a")


###########






# Convertir a numérico, suponiendo que los datos son directamente convertibles
cat_data$mean_temperature <- as.numeric(as.character(cat_data$mean_temperature))
cat_data$max_relative_humidity <- as.numeric(as.character(cat_data$max_relative_humidity))
cat_data$precipitation <- as.numeric(as.character(cat_data$precipitation))



cat_data <- cat_data[cat_data$timestamp >= as.POSIXct("2023-01-01"), ]









write.csv2(cat_data,("Out/DadesMeteoCat_temp.csv"), row.names = F)



# Grafic ####


library(dplyr)
library(ggplot2)
library(scales)
cat_data <- as.data.frame(cat_data)
# Assegura que la columna de timestamp està en format de data
cat_data$timestamp <- as.POSIXct(cat_data$timestamp, format = "%Y-%m-%d %H:%M:%S")

# Crear una nova columna 'month' per a facilitar el resum mensual
cat_data$month <- format(cat_data$timestamp, "%Y-%m")

# Agrupar per month i station_name, i calcular max i min temperatures
summary_data <- cat_data %>%
  group_by(month, station_name) %>%
  summarize(
    max_temp = max(mean_temperature),
    min_temp = min(mean_temperature),
    .groups = 'drop'  # Elimina la agrupació després de resumir
  )

# Unir els màxims i mínims amb les dades originals per a obtenir els timestamps corresponents
max_data <- cat_data %>%
  inner_join(summary_data, by = c("station_name", "month")) %>%
  filter(mean_temperature == max_temp)

min_data <- cat_data %>%
  inner_join(summary_data, by = c("station_name", "month")) %>%
  filter(mean_temperature == min_temp)

# Crear el gràfic
pp <- ggplot(cat_data, aes(x = timestamp, y = mean_temperature, color = station_name, group = station_name)) +
  geom_line() +
  geom_point(data = max_data, aes(x = timestamp, y = max_temp, color = station_name), size = 3, shape = 18) +
  geom_point(data = min_data, aes(x = timestamp, y = min_temp, color = station_name), size = 3, shape = 18) +
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
    title = "Temperatura Màxima i Mínima per Estació i Mes",
    x = "Data",
    y = "Temperatura (ºC)"
  )

pp



ggsave("Out/GraficsMeteoCat.jpg", plot = pp, width = 10, height = 7, dpi = 300)
ggsave(
  filename = "MODIFICAR PER LA TEVA CARPETA/Dades Obertes/GraficsMeteoCat.jpg.jpg", 
  plot = pp, 
  width = 15, 
  height = 7, 
  dpi = 300, 
  limitsize = FALSE
)














