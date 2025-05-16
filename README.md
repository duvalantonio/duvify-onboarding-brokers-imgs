# onboarding-brokers-imgs

- [onboarding-brokers-imgs](#onboarding-brokers-imgs)
  - [Guia de instalacion](#guia-de-instalacion)
  - [Guia de uso](#guia-de-uso)
  - [`onboarding_brokers_imgs.py`](#onboarding_brokers_imgspy)
    - [Instrucciones](#instrucciones)
  - [`retry_download_imgs.py`](#retry_download_imgspy)

Este proyecto contiene el codigo fuente para ejecutar el comando encargado de subir las images originales, de todas las propiedades que tiene Duvify, hacia el bucket `fotos-unidades-marca-agua`, con la correspondiente marca de agua del broker nuevo que contrata la plataforma.

Adicionalmente, tenemos el comando `inserte_nombre_comando` para volver a descargar ... (En proceso)

## Guia de instalacion

Para instalar el comando basta con descargar el repositorio e instalar los requerimientos de `requirements.txt`, se recomienda el uso de un entorno virtual de python:

```bash
cd onboarding-brokers-imgs
python3 -m venv my-venv
source my-venv/bin/activate
pip install -r requirements.txt
```

## Guia de uso

La tipica forma en que correras este comando es la siguiente:

```bash
python3 onboarding_brokers_imgs.py -d "duvify-brokers-fotos-unidades" -u "fotos-unidades-marca-agua" -br "nombre-empresa-broker" -k path/to/the/key/iam/file -w "url.marca-agua-broker.cl"
```

Esto descargara las imagenes del bucket `duvify-brokers-fotos-unidades` aplicandoles la marca de agua `url.marca-agua-broker.cl` para guardarlas en la carpeta `nombre-empresa-broker` en el bucket `fotos-unidades-marca-agua`.

>[!IMPORTANT]
>La duracion de ejecucion del comando depende de varios factores, como lo son:
>
> - Cantidad de fotos en el bucket desde donde se obtienes las imagenes originales, esto dado que de aca se recolectan todas las urls de las imagenes.
>
> - Cantidad de threads que se asignen. El posterior procesamiento con el cual se aplican las marcas de agua se realiza en paralelo, por tanto si se asignan una mayor cantidad de threads (siempre y cuando el PC lo permita), el procesamiento sera mucho mas rapido.

## `onboarding_brokers_imgs.py`

Este comando descarga las imagenes, que se encuentran en las carpetas `fotos`, desde un bucket, para luego aplicarles la marca de agua y subirlas en otro bucket especifico, siguiendo la misma estructura que el bucket de donde se descargaron, por ejemplo, si:

- El bucket desde donde se descargan las imagenes tiene la siguiente estructura para una carpeta:

    ```bash
    |__edificio-agustinas
        |__local-1
            |__fotos
                | agustinas-local-1-01.jpg
                | agustinas-local-1-02.jpg
                | agustinas-local-1-03.jpg
                | ...
    ```

- El bucket hacia el cual se subiran las imagenes con marca de agua del broker, tendra la siguiente estructura:

    ```bash
    |__nombre-empresa-broker
        |__edificio-agustinas
            |__local-1
                |__fotos
                    | agustinas-local-1-01.jpg
                    | agustinas-local-1-02.jpg
                    | agustinas-local-1-03.jpg
                    | ...
    ```

Comunmente la forma en que se utilizara el comando es pasandole el id del bucket donde se encuentran las imagenes originales (`duvify-brokers-fotos-unidades`), el id del bucket donde se subiran las imagenes con la marca de agua del nuevo cliente broker que se integra (`fotos-unidades-marca-agua`) y la marca de agua deseada.

### Instrucciones

Para ejecutar el comando es necesario realizar unos pasos extras, estos son:

1. Instalar Python 3.*
2. Instalar las dependencias que utiliza el comando (recomendado en un ambiente virtual):

    ```bash
    > pip3 install -r requirements.txt
    ```

3. Descargar la llave del user IAM `onboarding-broker` en cloud console para el proyecto `duvify brokers`.
4. Ejecutar el comando :).

El comando puede recibir varios parametros, sin embargo muchos de estos son opcionales, para ver la guia de ayuda del comando puedes ejecutar:

```bash
> python3 onboarding_brokers_imgs.py --help
```

Cada parametro posee una descripcion objetiva de lo que realiza. Aca va un resumen de lo que realiza cada parametro:

- `-d`: ID del bucket donde se encuentran las imagenes que queremos descargar, tipicamente sera el bucket `duvify-brokers-fotos-unidades`.
- `-u`: ID del bucket donde se subiran las imagenes procesadas, tipicamentes sera el bucket `fotos-unidades-marca-agua`.
- `-k`: Path/archivo que contiene la llave del usuario IAM con los permisos para acceder a los diferentes servicios de firebase storage, esto tipicamente es un archivo json que se descarga desde cloud console, para esto basta con ir a la seccion de IAM & Admin y buscar el usuario `onboarding-broker` para descargar su respetiva llave.
- `-br`: Nombre del broker para guardar las imagenes en una carpeta con el nombre respectivo.

Estos tres parametros son obligatorios a la hora de ejecutar el comando, los siguientes parametros son opcionales:

- `-w`: Url de la marca de agua que se utilizara para aplicar en todas las imagenes obtenidas del bucket `duvify-brokers-fotos-unidades` y subirlas al bucket `fotos-unidades-marca-agua`.

>[!IMPORTANT]
>Tal como se observa la marca de agua es un parametro opcional, es decir, si uno quiere puede simplemente ejecutar este comando para traspasar las fotos desde un bucket a otro, sin un proceso intermedio.

- `-f`: Archivo donde se guardan el historial de errores que puedan producirse durante la ejecucion del comando. Como tal no es necesario crearlo dado que se crea automaticamente al momento de la ejecucion, sin embargo si quieres asignar un archivo de tipo diferente al predeterminado (`.log`) puedes hacerlo.
- `-to`: Timeout para las requests que se realizan en toda la ejecucion del comando, tipicamente su uso esta destinado a asignarle un tiempo mayor al predeterminado si es que el recurso para aplicar marcas de agua se encuentra congestionado, lo que produce que las llamadas alcancen el tiempo de espera sin poder obtener un resultado.
- `-t`: Cantidad de threads que ocupara el PC para la ejecucion del comando, el valor predeterminado es 5.
- `-nt`: Numero de intentos que realizara el comando para poder obtener una respuesta satisfactoria al momento de aplicar la marca de agua usando el recurso `watermark.io`, estos numeros de intentos son para cada imagen.

>[!IMPORTANT]
>Esto no es la documentacion del comando, por tanto no es una guia total de lo que realiza, si quieres saber en especifico que tipo de dato recibe cada parametro ocupa el parametro `--help`.

## `retry_download_imgs.py`

Este comando se utiliza para volver a intentar a descargar las imagenes en las cuales se hayan producido errores al momento de aplicar la marca de agua, en la practica el uso de este comando sera la siguiente:

```bash
> python3 retry_download_imgs.py -d "duvify-brokers-fotos-unidades" -u "fotos-unidades-marca-agua" -br "nombre-empresa-broker" -k path/to/the/key/iam/file -w "url.marca-agua-broker.cl" -l path/to/logfile
```

>[!IMPORTANT]
> El proceso de descarga de las imagenes con la marca de agua aplicada demora un tiempo (dado que descarga archivos), sin embargo el proceso de subida de estas al bucket de firebase es mucho mas rapido dado que se encuentra paralelizado.
