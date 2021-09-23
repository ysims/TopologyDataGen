# Voxel Data Generation

## Generate Data

Install dependencies with `pip install -r requirements.txt`.

## Single Data

This generates a single voxel grid with the specified number of objects in it. It allows for drawing and saving of the data.

Run

```bash
python generate.py single [options]
```

Options include `--save` for saving the grid to a file, `--draw` for drawing the grid using matplotlib.
Other options involve the number of objects.

## Multi Dataset

This runs

## Load Grid

If you have a saved numpy array representing a voxel grid and want to view it using matplotlib, run:

```bash
python view_grid.py <path/to/grid.npy>
```

## Invert Grid

If you have a saved numpy array representing a voxel grid and want to save the inverted form of it, run

```bash
python save_inverted.py <input/grid/path.npy> <output/grid/path.npy> <grid_size>
```
