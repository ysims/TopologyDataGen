from abc import ABC, abstractmethod
import scipy.ndimage


class Shape(ABC):
    def _place(self, object_min_distance):
        # Create the object
        self._create_grid()
        grid_dilation = scipy.ndimage.binary_dilation(
            self.grid, scipy.ndimage.generate_binary_structure(3, 3), iterations=(object_min_distance + 1)
        )
        # Check intersect
        if (grid_dilation & self.full_grid).any():
            self.valid = False
        return

    @abstractmethod
    def _create_grid(self):
        pass

    @abstractmethod
    def _valid_edge(self, point):
        pass
