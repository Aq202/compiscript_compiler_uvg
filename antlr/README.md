
# Proyecto compiscript - Antlr

## Para correr el lab

* En esta carpeta (/antlr) deben crear un container interactivo en dónde van a correr los comandos de ANTLR:

  ```
  docker build --rm . -t compiscript-image
  ```

  ```
  docker run --rm -ti -v "${PWD}/program:/program" compiscript-image
  ```
  
* Luego de correr el comando de Docker, deberán de generar los archivos de Lexer y Parser de ANTLR con el siguiente comando:

  ```
  antlr -Dlanguage=Python3 -o ./gen Compiscript.g4
  ```
* Luego, usan el Driver para analizar el archivo de prueba:

  ```
  python3 main_analyzer.py prueba.txt
  ```
* El archivo prueba.txt es la entrada que va a ser analizada léxica y sintácticamente.
