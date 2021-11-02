# Topology Data Generation

You will need [Python](https://www.python.org/downloads/).

Created using: Python 3.7.6, Anaconda on Windows 10.

1. Install dependencies with `pip install -r requirements.txt`.

2. Run with

   ```bash
   python run.py <program> [options]
   ```

## Data Generation

Can be run with the `run` command with `<program>` set to `datagen`.

```bash
python run.py datagen <type> [options]
```

`<type>` is one of `single` or `dataset`.

General options for `datagen` are

| Option                 | Default                            | Description                               |
| ---------------------- | ---------------------------------- | ----------------------------------------- |
| `--cube_size`          | 50                                 | Size of the cavity-filled cube, cubed.    |
| `--shape_config`       | `./Objects/config/Shape.yaml`      | The path to the Shape config to use.      |
| `--random_walk_config` | `./Objects/config/RandomWalk.yaml` | The path to the RandomWalk config to use. |

### Single Data Generation

For generating one data sample.

```bash
python run.py datagen single [options]
```

Options are

| Option           | Default       | Description                                                      |
| ---------------- | ------------- | ---------------------------------------------------------------- |
| `--spheroid_num` | 0             | Number of spheroid cavities in the cube.                         |
| `--torus_num`    | 0             | Number of torus cavities in the cube.                            |
| `--torusN_num`   | 0             | Number of n-holed torus cavities in the cube.                    |
| `--island_num`   | 0             | Number of island cavities in the cube.                           |
| `--tunnel_num`   | 0             | Number of tunnel cavities in the cube.                           |
| `--octopus_num`  | 0             | Number of octopus cavities in the cube.                          |
| `--draw`         | False         | Draws the inverted form of the data in Matplotlib on creation.   |
| `--save`         | False         | Saves the data in a NumPy array on creation.                     |
| `--save_num`     | Random number | Saves the data with this name into the `all_data/single` folder. |

Example:

```bash
python run.py datagen single --spheroid_num 15 --tunnel_num 20 --draw --save --save_num 1
```

This will create a cube with 15 spheroid cavities and 20 tunnels. It will display the inverted cube in Matplotlib and then save the data in the `all_data/single` folder with the names `1_cube.npy`, `1_inverted_cube.npy` and `1_betti.yaml`. These are the files for the full grid, the inverted grid and the labels for the data respectively.

### Dataset Generation

For generating a set of many cubes. It takes an object type and generates x sub-datasets. For each sub-dataset, the number of cavities is constant.

```bash
python run.py datagen dataset <object> [options]
```

Options are

| Option          | Default | Description                                                                                   |
| --------------- | ------- | --------------------------------------------------------------------------------------------- |
| `--min_objects` | 1       | The number of object-shaped cavities in the sub-dataset with the smallest number of cavities. |
| `--max_objects` | 5       | The number of object-shaped cavities in the sub-dataset with the highest number of cavities.  |
| `--repeat`      | 1000    | Size of each sub-dataset.                                                                     |

Example:

```bash
python run.py datagen data spheroid --min_objects 5 --max_objects 30 --repeat 500
```

This will create a dataset with 26 sub-datasets, where the first sub-dataset has cubes with 5 spheroid cavities, the second sub-dataset has cubes with 6 spheroid cavities, until the last sub-dataset which has cubes with 30 spheroid cavities. Each sub-dataset is of size 500. In total, the size of the dataset would be 13,000 cubes.

## Data Augmentation

These methods change existing data in some way. They all have two arguments, the `input_file` and `output_file`. The first is the path to the data file to be changed and the second is the data path to save the new data to.

```bash
python run.py augment <type> <input_file> <output_file>
```

| Type                 | Description                                                                                                                                                                                                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `remove_internal`    | Removes all internal voxels. These are the voxels that are surrounded by other voxels. This is useful for visualisation of the data, since it is not possible to see these voxels and they may cause unnecessary memory overhead.                                            |
| `subsample`          | Subsamples the data such that around half of the data points are removed. Each point removed is not directly adjacent to another removed point, ignoring diagonals. This creates many small holes in the data which can improve performance of persistent homology software. |
| `invert`             | Inverts the grid. This is useful if you have a full grid that you would like to better visualise, or if you have an inverted grid that you would like to run persistent homology software on.                                                                                |
| `ripser_cpp_convert` | Converts the format of the grid from a NumPy array to a text file that lists the points. The text file can then be used in the original C++ version of Ripser, a persistent homology library.                                                                                |

## Visualisation

For visualising the data. There are two methods. The first uses Matplotlib.

```bash
python run.py visualise <input_file>
```

`<input_file>` is the path to the data file you would like to visualise.

The second method uses Blender (version 2.93.1).

1. [Download Blender](https://www.blender.org/download/) and launch it.
2. Open the file `src/scripts/visualisation/generate.py` in the text editor in Blender.
3. At the beginning of the file, edit the `folder_path` and `data_path` to point to the correct folders.
4. Run the script.

## Persistent Homology Libraries

For running data on persistent homology software. Gudhi is currently supported.

```bash
python run.py homology <type> <input_file> <filtration_type> [options]
```

| Argument | Default | Description |
| `type` | Required | `run` or `load`, for either running Gudhi on a dataset or loading Gudhi results to filter. |
| `input_file` | Required | File path of the data to input - data file or pickle file with Gudhi results. |
| `filtration_type` | Required | Either the Vietoris-Rips complex (`vietoris-rips`) or the Alpha complex (`alpha`). |
| `--save` | False | Saves the results of Gudhi in a pickle file. |
| `--output_file` | None | File path to save the Gudhi results to. Only required if `--save` is set. |
| `--filtering` | False | Set to filter the results of Gudhi and print the resulting homology. |
| `--vr_threshold` | None | If the Vietoris-Rips complex is chosen, this can be used to set the threshold/max_edge_length parameter. |
| `--b_0` | 1.0 | If filtering is set, this is the minimum lifetime that will be used when filtering Betti zero. |
| `--b_1` | 1.0 | If filtering is set, this is the minimum lifetime that will be used when filtering Betti one. |
| `--b_2` | 1.0 | If filtering is set, this is the minimum lifetime that will be used when filtering Betti two. |

Example:

```bash
python run.py homology gudhi run my_data.npy alpha --filtering --b0 2.5 --b1 0.8 --b2 1.5
```

This will run Gudhi with the Alpha complex on `my_data.npy` and filter it with minimum lifetimes of 2.5 for Betti zero, 0.8 for Betti one and 1.5 for Betti two.
