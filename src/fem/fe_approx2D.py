from scitools.std import plot, savefig, hold, axis, legend
import numpy as np
import sympy as sm

def mesh(nx, ny, x=[0,1], y=[0,1], diagonal='right'):
    """
    Return a 2D finite element mesh on a rectangle with
    extend x and y in the x and y directions.
    nx and ny are the divisions in the x and y directions.
    Return vertices and cells (local to global vertex number mapping).
    """
    if len(x) == 2:
        if nx is None:
            raise ValueError('box: interval in x %s, no nx set' % x)
        x = np.linspace(x[0], x[1], nx+1)
    else:
        nx = len(x)-1
    if len(y) == 2:
        if nx is None:
            raise ValueError('box: interval in y %s, no ny set' % y)
        y = np.linspace(y[0], y[1], ny+1)
    else:
        ny = len(y)-1

    if diagonal is None:
        vertices = np.zeros(((nx+1)*(ny+1), 2), dtype=np.float)
        cells = np.zeros((nx*ny, 4), dtype=np.int)
    elif diagonal == 'crossed':
        vertices = np.zeros(((nx+1)*(ny+1) + nx*ny, 2), dtype=np.float)
        cells = np.zeros((4*nx*ny, 3), dtype=np.int)
    else:
        vertices = np.zeros(((nx+1)*(ny+1), 2), dtype=np.float)
        cells = np.zeros((2*nx*ny, 3), dtype=np.int)

    vertex = 0
    for iy in xrange(ny+1):
        for ix in xrange(nx+1):
            vertices[vertex,:] = x[ix], y[iy]
            vertex += 1

    if diagonal == 'crossed':
        for iy in xrange(ny):
            for ix in xrange(nx):
                x_mid = 0.5*(x[ix+1] + x[ix])
                y_mid = 0.5*(y[iy+1] + y[iy])
                vertices[vertex,:] = x_mid, y_mid
                vertex += 1

    cell = 0
    if diagonal is None:
        for iy in xrange(ny):
            for ix in xrange(nx):
                v0 = iy*(nx + 1) + ix
                v1 = v0 + 1
                v2 = v0 + nx+1
                v3 = v1 + nx+1
                cells[cell,:] = v0, v1, v3, v2;  cell += 1

    elif diagonal == 'crossed':
        for iy in xrange(ny):
            for ix in xrange(nx):
                v0 = iy*(nx+1) + ix
                v1 = v0 + 1
                v2 = v0 + (nx+1)
                v3 = v1 + (nx+1)
                vmid = (nx+1)*(ny+1) + iy*nx + ix

                # Note that v0 < v1 < v2 < v3 < vmid.
                cells[cell,:] = v0, v1, vmid;  cell += 1
                cells[cell,:] = v0, v2, vmid;  cell += 1
                cells[cell,:] = v1, v3, vmid;  cell += 1
                cells[cell,:] = v2, v3, vmid;  cell += 1

    else:
        local_diagonal = diagonal
        # Set up alternating diagonal
        for iy in xrange(ny):
            if diagonal == "right/left":
                if iy % 2 == 0:
                    local_diagonal = "right"
                else:
                    local_diagonal = "left"

            if diagonal == "left/right":
                if iy % 2 == 0:
                    local_diagonal = "left"
                else:
                    local_diagonal = "right"
            for ix in xrange(nx):
                v0 = iy*(nx + 1) + ix
                v1 = v0 + 1
                v2 = v0 + nx+1
                v3 = v1 + nx+1

                if local_diagonal == "left":
                    cells[cell,:] = v0, v1, v2;  cell += 1
                    cells[cell,:] = v1, v2, v3;  cell += 1
                    if diagonal == "right/left" or diagonal == "left/right":
                        local_diagonal = "right"
                else:
                    cells[cell,:] = v0, v1, v3;  cell += 1
                    cells[cell,:] = v0, v2, v3;  cell += 1
                    if diagonal == "right/left" or diagonal == "left/right":
                        local_diagonal = "left"
    return vertices, cells


def plot_mesh(vertices, cells, materials=None, plotfile='tmp.png'):
    cell_vertex_coordinates = []
    for e in xrange(cells.shape[0]):
        local_vertex_numbers = cells[e,:]
        local_coordinates = vertices[local_vertex_numbers,:]
        cell_vertex_coordinates.append(local_coordinates)
    import matplotlib.cm as cm
    import matplotlib.collections as collections
    import matplotlib.pyplot as plt
    col = collections.PolyCollection(cell_vertex_coordinates)
    if materials is not None:
        col.set_array(materials)
        #col.set_cmap(cm.jet)
        #col.set_cmap(cm.gray_r)
        col.set_cmap(cm.hot_r)
    fig = plt.figure()
    ax = fig.gca()
    ax.add_collection(col)
    xmin, xmax = vertices[:,0].min(), vertices[:,0].max()
    ymin, ymax = vertices[:,1].min(), vertices[:,1].max()
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal')
    plt.savefig(plotfile + '.png')
    plt.savefig(plotfile + '.pdf')
    plt.show()

nx = 8; ny = 20

vertices, cells = mesh(nx, ny, x=[1,2], y=[0,1], diagonal='crossed')
Theta = np.pi/2
x = vertices[:,0]*np.cos(Theta*vertices[:,1])
y = vertices[:,0]*np.sin(Theta*vertices[:,1])
vertices[:,0] = x
vertices[:,1] = y
plot_mesh(vertices, cells, materials=np.zeros(cells.shape[0], dtype=np.int), plotfile='tmp_circle')
import sys
sys.exit(0)

nx = 4; ny = 3
for diagonal in None, 'right', 'left', 'right/left', 'left/right', 'crossed':
    vertices, cells = mesh(nx, ny, x=[0,3], y=[0,1], diagonal=diagonal)
    plot_mesh(vertices, cells, materials=np.zeros(cells.shape[0], dtype=np.int), plotfile=str('tmp_' + str(diagonal)).replace('/', '_'))

