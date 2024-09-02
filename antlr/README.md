# Compiscript project - Antlr

## Grammar compilation

* In this folder (/antlr) you must create an interactive container where you will run the ANTLR commands:

  ```
  docker build --rm . -t compiscript-image
  ```

  ```
  docker run --rm -ti -v "${PWD}/program:/program" compiscript-image
  ```
  
* After running the Docker command, you should generate the ANTLR Lexer and Parser files with the following command: 

  ```
  antlr -Dlanguage=Python3 -o ./gen Compiscript.g4
  ```
* Then, use the Driver to parse the test file:

  ```
  python3 main_analyzer.py prueba.txt
  ```
* The file test.txt is the input to be parsed lexically and syntactically.