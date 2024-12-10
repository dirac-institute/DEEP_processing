import lsst.pex.config as pexConfig
import lsst.pipe.base as pipeBase
import lsst.daf.base as dafBase
from lsst.pipe.tasks.selectImages import BestSeeingSelectVisitsConnections, BestSeeingQuantileSelectVisitsConfig, BestSeeingQuantileSelectVisitsTask


class DEEPSelectVisitsConnections(BestSeeingSelectVisitsConnections):
    goodVisits = pipeBase.connectionTypes.Output(
        doc="Selected visits to be coadded.",
        name="DEEPSelectedVisits",
        storageClass="StructuredDataDict",
        dimensions=("instrument", "tract", "patch", "skymap", "band"),
    )


class DEEPSelectVisitsConfig(BestSeeingQuantileSelectVisitsConfig, pipelineConnections=DEEPSelectVisitsConnections):
    timeSeparation = pexConfig.Field(
        doc="The time separation between visits in days",
        dtype=float,
        default=0.01,
    )


class DEEPSelectVisitsTask(BestSeeingQuantileSelectVisitsTask):
    ConfigClass = DEEPSelectVisitsConfig
    _DefaultName = 'DEEPSelectVisits'

    def run(self, visitSummaries, skyMap, dataId):
        # In order to store as a StructuredDataDict, convert list to dict
        results = super().run(visitSummaries, skyMap, dataId)
        goodVisits = results.goodVisits
        goodVisitsSorted = sorted(goodVisits)
        
        selectedVisits = {}
        last_mjd = 0
        times = []
        for visit in goodVisitsSorted:
            visitSummary = list(filter(lambda x : x.dataId['visit'] == visit, visitSummaries))[0].get()
            visitInfo = visitSummary[0].getVisitInfo()
            mjd = visitInfo.getDate().get(dafBase.DateTime.MJD)
            if mjd - last_mjd > self.config.timeSeparation:
                print("selecting", visit, "time separation", mjd - last_mjd)
                selectedVisits[visit] = True
                last_mjd = mjd
                times.append(mjd)

        print(goodVisits)
        print(len(goodVisits))
        print(selectedVisits)
        print(len(selectedVisits))
        print(times)
        # print(visitSummaries)
        # print(visitSummaries[0].get())
        # print(len(visitSummaries))
        goodVisits = selectedVisits
        return pipeBase.Struct(goodVisits=goodVisits)
