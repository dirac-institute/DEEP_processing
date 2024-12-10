from lsst.pipe.tasks import insertFakes, processCcdWithFakes

class ProcessCcdWithFakesConnections(processCcdWithFakes.ProcessCcdWithFakesConnections):
    fakeCats = cT.Input(
        doc="Set of catalogs of fake sources to draw inputs from. We "
            "concatenate the tract catalogs for detectorVisits that cover "
            "multiple tracts.",
        name="{fakesType}fakeSourceCat",
        storageClass="DataFrame",
        dimensions=("tract", "skymap"),
        deferLoad=True,
        multiple=True,
    )
