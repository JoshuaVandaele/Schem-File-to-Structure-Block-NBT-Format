# Schem File to Structure Block

This script converts a world edit schematic file to a structure block file.

## Requirements

You need to install the required packages specified in `requirements.txt` using pip.

```sh
pip install -r requirements.txt
```

## Usage

```sh
python schem2nbt.py <-i/--input schem_file.schem>
python schem2nbt.py <-i/--input schem_folder> -f
```

```sh
python schem2nbt.py -h

>  options:
>    -h, --help            show this help message and exit
>    -i INPUT, --input INPUT
>                          Path to the input schematic file.
>    -f, --folder          Whether to treat the input path as a file or a folder.
```
