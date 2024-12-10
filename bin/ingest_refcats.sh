butler register-dataset-type ${REPO} ps1_pv3_3pi_20170110 SimpleCatalog htm7
butler ingest-files ${REPO} ps1_pv3_3pi_20170110 refcats/ps1_pv3_3pi_20170110 ./data/refcats_ps1.ecsv

butler register-dataset-type ${REPO} gaia_dr3_20230707 SimpleCatalog htm7
butler ingest-files ${REPO} gaia_dr3_20230707 refcats/gaia_dr3_20230707 ./data/refcats_gaia_dr3.ecsv

butler register-dataset-type ${REPO} gaia_dr2_20200414 SimpleCatalog htm7
butler ingest-files ${REPO} gaia_dr2_20200414 refcats/gaia_dr2_20200414 ./data/refcats_gaia_dr2.ecsv

butler collection-chain ${REPO} refcats refcats/ps1_pv3_3pi_20170110 refcats/gaia_dr3_20230707 refcats/gaia_dr2_20200414
