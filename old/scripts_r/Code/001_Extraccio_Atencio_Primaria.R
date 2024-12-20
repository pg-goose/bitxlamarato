library(httr)
library(jsonlite)
library(dplyr)


# URL de l'API
url <- "https://analisi.transparenciacatalunya.cat/resource/fa7i-d8gc.json"

# Descarregar les dades utilitzant GET
resposta <- GET(url)

# Convertir el contingut JSON a un dataframe
df <- fromJSON(content(resposta, "text", encoding = "UTF-8"))




#-----#

library(httr)
library(jsonlite)
library(dplyr)

# URL de l'API
base_url <- "https://analisi.transparenciacatalunya.cat/resource/fa7i-d8gc.json"

# Definir el límit per consulta
limit <- 1000

data_inici <- "2023-01-01"

# Inicialitzar una llista per emmagatzemar totes les dades
resultats <- list()

# Inicialitzar el paràmetre d'offset i variable de control
offset <- 0
continue <- TRUE

# Bucle per descarregar les dades en fragments
while (continue) {
  # Forçar l'offset a un format numèric (evitar notació científica)
  offset_str <- format(offset, scientific = FALSE)
  
  # Crear la consulta amb el límit i l'offset
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
    # Imprimir el codi de resposta per depurar si hi ha un error
    print(content(resposta, "text"))
    stop("Error en la consulta API")
  }
}

# Combinar tots els fragments de dades en un únic dataframe
dades <- bind_rows(lapply(resultats, as.data.frame))



# Especificar la ruta corregida utilitzant barres inclinades ("/") i fent servir encoding UTF-8
write.csv2(
  dades, 
  file = "MODIFICAR PER LA TEVA CARPETA/Dades Obertes/Atenció_Primaria.csv", 
  row.names = FALSE, 
  fileEncoding = "UTF-8"
)



df <- dades

df %<>% filter(any == "2024")
df %<>% filter(nom_regio != "No disponible")

# Convertir la variable 'data' a format POSIXct (data amb hora inclosa)
df$data <- as.POSIXct(df$data, format = "%Y-%m-%dT%H:%M:%OS")

# Filtrar les dades a partir de l'1 d'agost de 2024
df <- df %>% filter(data >= as.POSIXct("2024-10-01"))




df$casos <- as.numeric(df$casos)



write.csv2(df,("Out_AtencioPrimaria/DadesAtencioPrimaria.csv"), row.names = F)



# GRAFIC ####




# Carregar les llibreries necessàries
library(dplyr)
library(ggplot2)
library(scales)

# Assegurar que la columna 'casos' és numèrica
df$casos <- as.numeric(df$casos)




# Agrupar les dades per data i regió per obtenir els casos acumulats per dia
df_acumulat <- df %>%
  group_by(data, nom_regio) %>%
  summarize(casos_acumulats = sum(casos, na.rm = TRUE), .groups = 'drop')

# Afegir la columna 'month' a df_acumulat per agrupar per mes posteriorment
df_acumulat <- df_acumulat %>%
  mutate(month = format(data, "%Y-%m"))

# Agrupar per mes i nom_regio, i calcular el valor màxim dels casos acumulats per dia
summary_data <- df_acumulat %>%
  group_by(month, nom_regio) %>%
  summarize(max_casos_acumulats = max(casos_acumulats, na.rm = TRUE), .groups = 'drop')

# Unir els màxims amb les dades originals per obtenir els timestamps corresponents
max_data <- df_acumulat %>%
  inner_join(summary_data, by = c("nom_regio", "month")) %>%
  filter(casos_acumulats == max_casos_acumulats)

# Crear el gràfic amb totes les línies de casos acumulats per dia i els punts màxims per mes
# Usar una paleta continua amb molts colors

# Definir una paleta personalitzada
# Definir una paleta personalitzada de 10 colors
colors_personalitzats <- c("#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0", 
                           "#FFB533", "#8A33FF", "#FF3333", "#33FFB2", "#FF33FF")

pp <- ggplot(df_acumulat, aes(x = data, y = casos_acumulats, color = nom_regio, group = nom_regio)) +
  geom_line() +
  geom_point(data = max_data, aes(x = data, y = max_casos_acumulats, color = nom_regio), size = 3, shape = 18) +
  scale_x_datetime(labels = date_format("%d %b %y"), breaks = date_breaks("1 month")) +
  scale_color_manual(values = colors_personalitzats) +  # Paleta personalitzada
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 26, face = "bold"),
    axis.title = element_text(size = 22, face = "bold"),
    axis.text = element_text(size = 18),
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size = 16)
  ) +
  labs(
    title = "Evolució dels Casos Acumulats per Regió i Dia",
    x = "",
    y = "Casos Acumulats"
  )




# Mostrar el gràfic
print(pp)



# Guardar el gràfic amb dimensions més equilibrades
ggsave("Out_AtencioPrimaria/Grafic Atenció Primària.jpg", plot = pp, width = 20, height = 10, dpi = 300, limitsize = FALSE)
# Guardar el gràfic amb ggsave
ggsave(
  filename = "MODIFICAR PER LA TEVA CARPETA/Dades Obertes/Grafic Atenció Primària.jpg", 
  plot = pp, 
  width = 15, 
  height = 7, 
  dpi = 300, 
  limitsize = FALSE
)




