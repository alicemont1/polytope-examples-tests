# SUBMODULE_PATH = "test"
# REPO_URL = "https://github.com/alicemont1/test"
# REFERENCE_BRANCH = "main"

SUBMODULE_PATH = "polytope-examples"
REPO_URL = "https://github.com/destination-earth-digital-twins/polytope-examples"
REFERENCE_BRANCH = "notebook-tests"
IMG_COMPARE_THRESHOLD = 1
IS_LIVE_REQUEST = False

BASE_IGNORES = (
    '/metadata',
    '/cells/*/metadata',
    '/cells/*/execution_count',
    '/cells/*/source',
    '/cells/*/id',
    '/cells/*/outputs/*/execution_count',
    '/cells/*/outputs/*/data/text/html',
)

TAG_IGNORES = {
    "skip-text-plain": "/cells/{idx}/outputs/*/data/text/plain",
    "skip-outputs": "/cells/{idx}/outputs",
    "skip-image": "/cells/{idx}/outputs/*/data/image/png",
}

TAG_IMAGE_CHECKS = {"check-image"}

TEST_MODIFIED_NOTEBOOKS = False

NOTEBOOKS = [
    'climate-dt/climate-dt-earthkit-example.ipynb',
    'climate-dt/climate-dt-earthkit-aoi-example.ipynb',
    'climate-dt/climate-dt-earthkit-area-example.ipynb',
    'climate-dt/climate-dt-earthkit-example-domain.ipynb',
    'climate-dt/climate-dt-earthkit-fe-boundingbox.ipynb',
    'climate-dt/climate-dt-earthkit-fe-polygon.ipynb',
    'climate-dt/climate-dt-earthkit-fe-story-nudging.ipynb',
    'climate-dt/climate-dt-earthkit-fe-timeseries.ipynb',
    'climate-dt/climate-dt-earthkit-fe-trajectory.ipynb',
    'climate-dt/climate-dt-earthkit-fe-verticalprofile.ipynb',
    'climate-dt/climate-dt-earthkit-grid-example.ipynb',
    'climate-dt/climate-dt-earthkit-healpix-interpolate.ipynb',
    'climate-dt/climate-dt-healpix-data.ipynb',
    'climate-dt/climate-dt-healpix-ocean-example.ipynb',

    'extremes-dt/extremes-dt-earthkit-example-domain.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-boundingbox.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-country.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-polygon.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-timeseries.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-trajectory.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-trajectory4d.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-verticalprofile.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-fe-wave.ipynb',
    'extremes-dt/extremes-dt-earthkit-example-regrid.ipynb',
    'extremes-dt/extremes-dt-earthkit-example.ipynb',
]
