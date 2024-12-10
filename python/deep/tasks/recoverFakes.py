from lsst.meas.base import forcedPhotCcd
import lsst.pipe.base.connectionTypes as cT
import numpy as np

class RecoverFakesConnections(forcedPhotCcd.ForcedPhotCcdFromDataFrameConnections):
    refCat = cT.Input(
        doc="Catalog of positions at which to force photometry.",
        name="DEEP_fakes_prepared",
        storageClass="DataFrame",
        dimensions=["instrument", "visit", "detector"],
        multiple=True,
        deferLoad=True,
    )
    measCat = cT.Output(
        doc="Output forced photometry catalog.",
        name="forced_fakes",
        storageClass="SourceCatalog",
        dimensions=["instrument", "visit", "detector"],
    )
    outputSchema = cT.InitOutput(
        doc="Schema for the output forced measurement catalogs.",
        name="forced_fakes_schema",
        storageClass="SourceCatalog",
    )    

class RecoverFakesConfig(forcedPhotCcd.ForcedPhotCcdFromDataFrameConfig, pipelineConnections=RecoverFakesConnections):
    pass
    

class RecoverFakesTask(forcedPhotCcd.ForcedPhotCcdFromDataFrameTask):
    _DefaultName = "recoverFakes"
    ConfigClass = RecoverFakesConfig

    def run(self, **inputs):
        print(len(inputs['refCat']))
        print(inputs['refCat'])
        return super().run(**inputs)

    # def runQuantum(self, butlerQC, inputRefs, outputRefs):
    #     inputs = butlerQC.get(inputRefs)

    #     refCat = []
    #     for cat in inputs['refCat']:
    #         cat['diaObjectId'] = cat.apply(lambda x : "_".join(map(str, [x['visit'], x['ORBITID']])), axis=1)
    #         cat['ra'] = cat['ra'] * 180/np.pi
    #         cat['dec'] = cat['dec'] * 180/np.pi
    #         refCat.append(cat)
        
    #     inputs['refCat'] = refCat

    #     # When run with dataframes, we do not need a reference wcs.
    #     inputs['refWcs'] = None

    #     # Connections only exist if they are configured to be used.
    #     skyCorr = inputs.pop('skyCorr', None)
    #     if self.config.useGlobalExternalSkyWcs:
    #         externalSkyWcsCatalog = inputs.pop('externalSkyWcsGlobalCatalog', None)
    #     else:
    #         externalSkyWcsCatalog = inputs.pop('externalSkyWcsTractCatalog', None)
    #     if self.config.useGlobalExternalPhotoCalib:
    #         externalPhotoCalibCatalog = inputs.pop('externalPhotoCalibGlobalCatalog', None)
    #     else:
    #         externalPhotoCalibCatalog = inputs.pop('externalPhotoCalibTractCatalog', None)
    #     finalizedPsfApCorrCatalog = inputs.pop('finalizedPsfApCorrCatalog', None)

    #     inputs['exposure'] = self.prepareCalibratedExposure(
    #         inputs['exposure'],
    #         skyCorr=skyCorr,
    #         externalSkyWcsCatalog=externalSkyWcsCatalog,
    #         externalPhotoCalibCatalog=externalPhotoCalibCatalog,
    #         finalizedPsfApCorrCatalog=finalizedPsfApCorrCatalog,
    #         visitSummary=inputs.pop("visitSummary"),
    #     )

    #     self.log.info("Filtering ref cats: %s", ','.join([str(i.dataId) for i in inputs['refCat']]))
    #     if inputs["exposure"].getWcs() is not None:
    #         refCat = self.df2RefCat([i.get(parameters={"columns": ['diaObjectId', 'ra', 'dec']})
    #                                  for i in inputs['refCat']],
    #                                 inputs['exposure'].getBBox(), inputs['exposure'].getWcs())
    #         inputs['refCat'] = refCat
    #         # generateMeasCat does not use the refWcs.
    #         inputs['measCat'], inputs['exposureId'] = self.generateMeasCat(
    #             inputRefs.exposure.dataId, inputs['exposure'], inputs['refCat'], inputs['refWcs']
    #         )
    #         # attachFootprints only uses refWcs in ``transformed`` mode, which is not
    #         # supported in the DataFrame-backed task.
    #         self.attachFootprints(inputs["measCat"], inputs["refCat"], inputs["exposure"], inputs["refWcs"])
    #         outputs = self.run(**inputs)

    #         butlerQC.put(outputs, outputRefs)
    #     else:
    #         self.log.info("No WCS for %s.  Skipping and no %s catalog will be written.",
    #                       butlerQC.quantum.dataId, outputRefs.measCat.datasetType.name)

# class RecoverFakesConnections(PipelineTaskConnections,
#                                dimensions=("instrument", "visit", "detector", "skymap", "tract")):
#     skyMap = cT.Input(
#         doc="Skymap that defines tracts",
#         name=BaseSkyMap.SKYMAP_DATASET_TYPE_NAME,
#         dimensions=("skymap",),
#         storageClass="SkyMap",
#     )

#     partitionedFakes = cT.Output(
#         doc="Fakes partitioned by tract",
#         name="DEEP_fakes_partitioned",
#         storageClass="DataFrame",
#         dimensions=("skymap", "tract"),
#         multiple=True,
#     )

#     exposure = cT.Input(
#         doc="Input exposure to perform photometry on.",
#         name="calexp",
#         storageClass="ExposureF",
#         dimensions=["instrument", "visit", "detector"],
#     )

#     measCat = cT.Output(
#         doc="Output forced photometry catalog.",
#         name="fakes_forced_phot",
#         storageClass="DataFrame",
#         dimensions=["instrument", "visit", "detector", "skymap", "tract"],
#     )

# class RecoverFakesConfig(pipeBase.PipelineTaskConfig,
#                           pipelineConnections=RecoverFakesConnections):
#     measurement = lsst.pex.config.ConfigurableField(
#         target=ForcedMeasurementTask,
#         doc="subtask to do forced measurement"
#     )

# class RecoverFakesTask(pipeBase.PipelineTask):
#     ConfigClass = ForRecoverFakesConfigcedPhotCcdConfig
#     _DefaultName = "recoverFakes"

#     def run(self, ):
#         pass

#     def runQuantum(self, butlerQC, inputRefs, outputRefs):
#         inputs = butlerQC.get(inputRefs)
#         outputs = self.run(**inputs)
#         if outputs:
#             butlerQC.put(outputs, outputRefs)

