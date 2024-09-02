# Project Name

## Description
Compiscript compilator.

## Installation
1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```sh
    cd <project-directory>
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Run the application:
    ```sh
    python main.py
    ```

## Project Structure

* **main.py**: main program file. When executed, it opens a code editor in which the semantic analysis of compiscript programs can be executed.

* **/compiler_source_code**: stores all the files related to the semantic analysis. Inside this one are defined the symbol table, the different types of the language, the listeners for the path and validation of the nodes of the syntactic tree, etc.

* **/code_editor**: stores files related to the graphical interface of the compiscript code editor.

* **/antlr**: stores files related to the compilation of the compiscript grammar. To perform the compilation, you must run a container of the image defined there. For more information on the compilation read [instructions for compiling grammar with ANTLR](./antlr/README.md)

## Dependencies
- Python 3.x
- PyQt5
- QSyntax
- antlr4-python3-runtime
- anytree (debbugging)
