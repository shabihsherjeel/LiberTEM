import io
import os
import numpy as np
import nbformat
from temp_utils import _get_hdf5_params
from libertem.udf.FEM import FEMUDF
from libertem.web.notebook_generator.notebook_generator import notebook_generator
from nbconvert.preprocessors import ExecutePreprocessor


def test_fem_analysis(hdf5_ds_2, tmpdir_factory, lt_ctx):
    datadir = tmpdir_factory.mktemp('template_tests')

    conn = {'connection': {'type': 'local'}}
    path = hdf5_ds_2.path
    dataset = _get_hdf5_params(path)

    params = {
        'shape': 'ring',
        'cx': 1,
        'cy': 1,
        'ri': 0,
        'ro': 1,
    }

    analysis = [{
            "analysisType": 'FEM',
            "parameters": params
    }]

    notebook = notebook_generator(conn, dataset, analysis, save=True)
    notebook = io.StringIO(notebook.getvalue())
    nb = nbformat.read(notebook, as_version=4)
    ep = ExecutePreprocessor(timeout=600)
    out = ep.preprocess(nb, {"metadata": {"path": datadir}})
    data_path = os.path.join(datadir, 'fem_result.npy')
    results = np.load(data_path)

    analysis = FEMUDF(center=(1,1), rad_in=0, rad_out=1)
    expected = lt_ctx.run_udf(dataset=hdf5_ds_2, udf=analysis)
    assert np.allclose(
        results,
        expected['intensity'],
    )
