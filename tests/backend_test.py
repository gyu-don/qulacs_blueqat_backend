from numpy.testing import assert_almost_equal
from blueqat import Circuit
import qulacs_blueqat_backend

qulacs_blueqat_backend.register_backend()

def test_circuit1():
    c = Circuit().h[:].z[6]
    assert_almost_equal(c.run_with_numpy(), c.run_with_qulacs())

def test_circuit2():
    c = Circuit().x[2].x[4]
    assert_almost_equal(c.run_with_numpy(), c.run_with_qulacs())
