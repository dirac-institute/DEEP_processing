import logging
from parsl.providers import LocalProvider, SlurmProvider

logging.basicConfig()
logger = logging.getLogger(__name__)

class DefaultsProvider():
    defaults = dict()
    def __init__(self, *args, **kwargs):
        for k, v in self.defaults.items():
            if k not in kwargs:
                kwargs[k] = v
        super().__init__(*args, **kwargs)

class KloneProvider(DefaultsProvider, SlurmProvider):
    defaults = dict(
        cpus_per_node=1,
        mem_per_node=8,
        init_blocks=0,
        min_blocks=0,
        parallelism=1,
        walltime="4:00:00",
        exclusive=False
    )

    def __init__(self, *args, **kwargs):
        for k, v in self.defaults.items():
            if k not in kwargs:
                kwargs[k] = v
        super().__init__(*args, **kwargs)        


class KloneAstroProvider(KloneProvider):
    defaults = dict(
        partition="astro",
        account="astro",
        max_blocks=4,
    ) | KloneProvider.defaults

class KloneCheckpointProvider(KloneProvider):
    defaults = KloneProvider.defaults | dict(
        partition="ckpt-all",
        account="astro-ckpt",
        max_blocks=64,
    )

class EpycProvider(DefaultsProvider, LocalProvider):
    defauts = DefaultsProvider.defaults | dict(
        min_blocks=1,
        max_blocks=48,
    )

