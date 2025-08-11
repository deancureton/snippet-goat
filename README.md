# snippet-goat

a simple and powerful way to manage your latex snippets for obsidian and vs code from a single source of truth

## what is this?

this project provides a unified system for managing your code snippets. all your snippets live in a single, easy-to-read `snippets.yaml` file. a python script then compiles this file into the platform-specific formats required by obsidian-latex-suite and vs code's hypersnips extension. it's built to be flexible, allowing for platform-specific overrides, shared variables, and more.

## prerequisites

this project is built around two key tools; you'll need them installed and configured to get started. if you aren't already using them both there's probably no reason to be reading this right now.

-   [obsidian-latex-suite](https://github.com/artisticat1/obsidian-latex-suite)
-   [hypersnips](https://marketplace.visualstudio.com/items?itemName=draivin.hsnips)

## setup

in obsidian-latex-suite's settings:
-   enable `Load snippets from file or folder`
-   enable `Load snippet variables from file or folder`
-   take note of the file paths you choose for both of these settings

in vs code:
-   create an empty `latex.hsnips` file in your hypersnips snippets directory
-   take note of its file path

now, in the `.env` file in the root of this project, fill in the absolute paths you noted in the previous step. here's what your `.env` file should look like:

```
# .env file
OBSIDIAN_SNIPPETS_PATH="/path/to/your/obsidian/snippets.js"
OBSIDIAN_VARIABLES_PATH="/path/to/your/obsidian/variables.json"
LATEX_SNIPPETS_PATH="/path/to/your/latex/snippets.hsnips"
```

## building snippets

assuming you have python 3 installed (you probably do), open your terminal and run

```
make snippets
```

this command will create a local python virtual environment, install the necessary dependencies, and generate your snippet files in the locations you specified.

## cleaning up

to remove all generated files (at the paths specified in your `.env`) and the python virtual environment, simply run

```
make clean
```

that's pretty much it, enjoy! in the existing `snippets.yaml` i've provided the snippets i actually use in my setup, if that's useful. they're a combination of the default obsidian-latex-suite snippets, snippets from [here](https://github.com/Einlar/latex_snippets/blob/master/hsnips/latex.hsnips), and my own personal snippets.