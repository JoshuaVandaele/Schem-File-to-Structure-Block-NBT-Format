# Schem File to Structure Block

This script converts a world edit schematic file to a structure block file.

## Requirements

Make sure you have the appropriate packages installed. You can install them by running the command:

```sh
pip install -r requirements.txt
```

## Usage

To convert a schematic file, use the following command:

```sh
python schem2nbt.py -i <schem_file>
```

To convert all schematic files in a folder, use the following command:

```sh
python schem2nbt.py -i <schem_folder> -f
```

## Command Line Options

The script accepts the following command line options:

```sh
python schem2nbt.py -h

> usage: schem2nbt.py [-h] -i INPUT [-o OUTPUT] [-f]
>
> Converts WorldEdit schematic files to Minecraft Structure files.
>
> options:
>   -h, --help            show this help message and exit
>   -i INPUT, --input INPUT
>                         Path to the input schematic file or folder.
>   -o OUTPUT, --output OUTPUT
>                         Path to the output nbt file or folder.
>   -f, --folder          Whether to treat the input path as a file or a folder.
```

Feel free to reach out if you have any questions or need further assistance.
