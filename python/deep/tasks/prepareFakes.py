import lsst.pipe.base as pipeBase
from lsst.pipe.base import PipelineTask, PipelineTaskConfig, PipelineTaskConnections
import lsst.pipe.base.connectionTypes as cT
from lsst.skymap import BaseSkyMap
import pandas as pd
from astropy.table import vstack, Table
import numpy as np

class PrepareFakesConnections(PipelineTaskConnections, dimensions=("skymap", "tract", "instrument", "visit", "detector")):
    partitionedFakes = cT.Input(
        doc="Fakes partitioned by tract",
        name="DEEP_fakes_partitioned",
        storageClass="DataFrame",
        dimensions=("skymap", "tract"),
    )

    exposure = cT.Input(
        doc="exposure",
        name="calexp",
        storageClass="ExposureF",
        dimensions=("instrument", "visit", "detector"),
        deferLoad=True,
    )

    preparedFakes = cT.Output(
        doc="Fakes prepared by tract",
        name="DEEP_fakes_prepared",
        storageClass="DataFrame",
        dimensions=("instrument", "visit", "detector"),
    )

class PrepareFakesConfig(PipelineTaskConfig, pipelineConnections=PrepareFakesConnections):
    pass

class PrepareFakesTask(PipelineTask):
    ConfigClass = PrepareFakesConfig
    _DefaultName = "prepareFakes"

    def run(self, partitionedFakes, exposure):
        if len(partitionedFakes) == 0:
            return None
        partitionedFakes = partitionedFakes[exposure.ref.dataId['visit'] == partitionedFakes['visit']]
        partitionedFakes = partitionedFakes[exposure.ref.dataId['detector'] == partitionedFakes['CCDNUM']]
        partitionedFakes['diaObjectId'] = partitionedFakes.apply(lambda x : "_".join(map(str, [x['visit'], x['ORBITID']])), axis=1)
        partitionedFakes['ra'] = partitionedFakes['ra'] * 180/np.pi
        partitionedFakes['decl'] = partitionedFakes['dec'] * 180/np.pi
        return pipeBase.Struct(preparedFakes=partitionedFakes)

    def runQuantum(self, butlerQC, inputRefs, outputRefs):
        inputs = butlerQC.get(inputRefs)
        # print(inputs)
        outputs = self.run(**inputs)
        if outputs:
            butlerQC.put(outputs, outputRefs)

