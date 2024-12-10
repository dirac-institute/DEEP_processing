from astro_metadata_translator.translator import cache_translation, MetadataTranslator

__all__ = ("DEEPMetadataTranslator",)

class DEEPMetadataTranslator(MetadataTranslator):
    @cache_translation
    def to_observing_day(self) -> int:
        """Return the YYYYMMDD integer corresponding to the observing day.

        Base class implementation uses the TAI date of the start of the
        observation.

        Returns
        -------
        day : `int`
            The observing day as an integer of form YYYYMMDD. If the header
            is broken and is unable to obtain a date of observation, ``0``
            is returned and the assumption is made that the problem will
            be caught elsewhere.
        """
        datetime_begin = self.to_datetime_begin()
        print("test")
        if datetime_begin is None:
            return 0
        return int(datetime_begin.tai.strftime("%Y%m%d"))
