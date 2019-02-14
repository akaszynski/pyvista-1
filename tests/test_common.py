import vtk
import pytest
import vtki
from vtki import examples
import numpy as np

grid = vtki.UnstructuredGrid(examples.hexbeamfile)


def test_point_arrays():
    key = 'test_array'
    grid.point_arrays[key] = np.arange(grid.n_points)
    assert key in grid.point_arrays

    orig_value = grid.point_arrays[key][0]/1.0
    grid.point_arrays[key][0] += 1
    assert orig_value == grid._point_scalar(key)[0] -1

    del grid.point_arrays[key]
    assert key not in grid.point_arrays

    grid.point_arrays[key] = np.arange(grid.n_points)
    assert key in grid.point_arrays


def test_point_arrays_bad_value():
    with pytest.raises(TypeError):
        grid.point_arrays['new_array'] = None

    with pytest.raises(Exception):
        grid.point_arrays['new_array'] = np.arange(grid.n_points - 1)


def test_cell_arrays():
    key = 'test_array'
    grid.cell_arrays[key] = np.arange(grid.n_cells)
    assert key in grid.cell_arrays

    orig_value = grid.cell_arrays[key][0]/1.0
    grid.cell_arrays[key][0] += 1
    assert orig_value == grid.cell_arrays[key][0] -1

    del grid.cell_arrays[key]
    assert key not in grid.cell_arrays

    grid.cell_arrays[key] = np.arange(grid.n_cells)
    assert key in grid.cell_arrays


def test_cell_arrays_bad_value():
    with pytest.raises(TypeError):
        grid.cell_arrays['new_array'] = None

    with pytest.raises(Exception):
        grid.cell_arrays['new_array'] = np.arange(grid.n_cells - 1)


def test_copy():
    grid_copy = grid.copy(deep=True)
    grid_copy.points[0] = np.nan
    assert not np.any(np.isnan(grid.points[0]))

    grid_copy_shallow = grid.copy(deep=False)
    grid_copy.points[0] += 0.1
    assert np.all(grid_copy_shallow.points[0] == grid.points[0])


def test_transform():
    trans = vtk.vtkTransform()
    trans.RotateX(30)
    trans.RotateY(30)
    trans.RotateZ(30)
    trans.Translate(1, 1, 2)
    trans.Update()

    grid_a = grid.copy()
    grid_b = grid.copy()
    grid_c = grid.copy()
    grid_a.transform(trans)
    grid_b.transform(trans.GetMatrix())
    grid_c.transform(vtki.trans_from_matrix(trans.GetMatrix()))
    assert np.allclose(grid_a.points, grid_b.points)
    assert np.allclose(grid_a.points, grid_c.points)


def test_transform_errors():
    with pytest.raises(TypeError):
        grid.transform(None)

    with pytest.raises(Exception):
        grid.transform(np.array([1]))


def test_translate():
    grid_copy = grid.copy()
    xyz = [1, 1, 1]
    grid_copy.translate(xyz)

    grid_points = grid.points.copy() + np.array(xyz)
    assert np.allclose(grid_copy.points, grid_points)


def test_rotate_x():
    angle = 30
    trans = vtk.vtkTransform()
    trans.RotateX(angle)
    trans.Update()

    trans_filter = vtk.vtkTransformFilter()
    trans_filter.SetTransform(trans)
    trans_filter.SetInputData(grid)
    trans_filter.Update()
    grid_a = vtki.UnstructuredGrid(trans_filter.GetOutput())

    grid_b = grid.copy()
    grid_b.rotate_x(angle)
    assert np.allclose(grid_a.points, grid_b.points)


def test_rotate_y():
    angle = 30
    trans = vtk.vtkTransform()
    trans.RotateY(angle)
    trans.Update()

    trans_filter = vtk.vtkTransformFilter()
    trans_filter.SetTransform(trans)
    trans_filter.SetInputData(grid)
    trans_filter.Update()
    grid_a = vtki.UnstructuredGrid(trans_filter.GetOutput())

    grid_b = grid.copy()
    grid_b.rotate_y(angle)
    assert np.allclose(grid_a.points, grid_b.points)


def test_rotate_z():
    angle = 30
    trans = vtk.vtkTransform()
    trans.RotateZ(angle)
    trans.Update()

    trans_filter = vtk.vtkTransformFilter()
    trans_filter.SetTransform(trans)
    trans_filter.SetInputData(grid)
    trans_filter.Update()
    grid_a = vtki.UnstructuredGrid(trans_filter.GetOutput())

    grid_b = grid.copy()
    grid_b.rotate_z(angle)
    assert np.allclose(grid_a.points, grid_b.points)


def test_make_points_double():
    grid_copy = grid.copy()
    grid_copy.points = grid_copy.points.astype(np.float32)
    assert grid_copy.points.dtype == np.float32
    grid_copy.points_to_double()
    assert grid_copy.points.dtype == np.double


def test_invalid_points():
    with pytest.raises(TypeError):
        grid.points = None


def test_points_np_bool():
    bool_arr = np.zeros(grid.n_points, np.bool)
    grid.point_arrays['bool_arr'] = bool_arr
    bool_arr[:] = True
    assert grid.point_arrays['bool_arr'].all()
    assert grid._point_scalar('bool_arr').all()
    assert grid._point_scalar('bool_arr').dtype == np.bool


def test_cells_np_bool():
    bool_arr = np.zeros(grid.n_cells, np.bool)
    grid.cell_arrays['bool_arr'] = bool_arr
    bool_arr[:] = True
    assert grid.cell_arrays['bool_arr'].all()
    assert grid._cell_scalar('bool_arr').all()
    assert grid._cell_scalar('bool_arr').dtype == np.bool


def test_cells_uint8():
    arr = np.zeros(grid.n_cells, np.uint8)
    grid.cell_arrays['arr'] = arr
    arr[:] = np.arange(grid.n_cells)
    assert np.allclose(grid.cell_arrays['arr'], np.arange(grid.n_cells))


def test_points_uint8():
    arr = np.zeros(grid.n_points, np.uint8)
    grid.point_arrays['arr'] = arr
    arr[:] = np.arange(grid.n_points)
    assert np.allclose(grid.point_arrays['arr'], np.arange(grid.n_points))


def test_bitarray_points():
    n = grid.n_points
    vtk_array = vtk.vtkBitArray()
    np_array = np.empty(n, np.bool)
    vtk_array.SetNumberOfTuples(n)
    vtk_array.SetName('bint_arr')
    for i in range(n):
        value = i%2
        vtk_array.SetValue(i, value)
        np_array[i] = value

    grid.GetPointData().AddArray(vtk_array)
    assert np.allclose(grid.point_arrays['bint_arr'], np_array)


def test_bitarray_cells():
    n = grid.n_cells
    vtk_array = vtk.vtkBitArray()
    np_array = np.empty(n, np.bool)
    vtk_array.SetNumberOfTuples(n)
    vtk_array.SetName('bint_arr')
    for i in range(n):
        value = i%2
        vtk_array.SetValue(i, value)
        np_array[i] = value

    grid.GetCellData().AddArray(vtk_array)
    assert np.allclose(grid.cell_arrays['bint_arr'], np_array)


def test_html_repr():
    """
    This just tests to make sure no errors are thrown on the HTML
    representation method for Common datasets.
    """
    repr_html = grid._repr_html_()
    assert repr_html is not None


def test_texture():
    """Test adding texture coordinates"""
    # create a rectangle vertices
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 0.5, 0],
                         [0, 0.5, 0],])

    # mesh faces
    faces = np.hstack([[3, 0, 1, 2],
                       [3, 0, 3, 2]]).astype(np.int8)

    # Create simple texture coordinates
    t_coords = np.array([[0, 0],
                        [1, 0],
                        [1, 1],
                        [0, 1]])
    # Create the poly data
    mesh = vtki.PolyData(vertices, faces)
    # Attempt setting the texture coordinates
    mesh.t_coords = t_coords
    # now grab the texture coordinates
    foo = mesh.t_coords
    assert np.allclose(foo, t_coords)


# def test_active_v
