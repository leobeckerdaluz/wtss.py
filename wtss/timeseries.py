#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""

from .utils import render_html


class TimeSeries(dict):
    """A class that represents a time series in WTSS.

    .. note::

        For more information about time series definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, coverage, data):
        """Create a TimeSeries object associated to a coverage.

        Args:
            coverage (Coverage): The coverage that this time series belongs to.
        """
        #: Coverage: The associated coverage.
        self._coverage = coverage

        super(TimeSeries, self).__init__(data or {})

        # Verify if query returned timeseries
        success_query = True if len(self['results']) > 0 else False
        setattr(self, 'success_query', success_query)

        # Add all timeseries from an attribute as object property
        if success_query:
            # Get attribute names and first timeseries
            values = dict()
            attributes = [attrs for attrs in self['results'][0]['time_series']['values'].items()]
            for attr_name, values0 in attributes:
                values[attr_name] = [values0]
            # Get remaining timeseries
            for i in range(1, len(self['results'])):
                attributes = [attrs for attrs in self['results'][i]['time_series']['values'].items()]
                for attr_name, timeserie in attributes:
                    values[attr_name].append(timeserie)
            # Create self attributes with the results
            for attr_name, all_timeseries in values.items():
                setattr(self, attr_name, all_timeseries)


    @property
    def number_of_pixels(self):
        """Return the number of pixels computed in timeseries."""
        return len(self['results'])

    @property
    def timeline(self):
        """Return the timeline associated to the time series."""
        return self['results'][0]['time_series']['timeline'] if self.success_query else None


    @property
    def success_request(self):
        """Return a list with attribute names."""
        return True if self.success_query else False
        

    @property
    def attributes(self):
        """Return a list with attribute names."""
        return [attr for attr in self['results'][0]['time_series']['values']] if self.success_query else None


    def values(self, attr_name):
        """Return the time series for the given attribute."""
        return getattr(self, attr_name)


    def pandas_dataframe(self):
        """Create a pandas dataframe with timeseries data.

        Raises:
            ImportError: If Pandas or Maptplotlib could not be imported.
        """
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
        except:
            raise ImportError('Cannot import one of the following libraries: [pandas, matplotlib].')

        # Build the dataframe in a tibble format
        attrs = []
        aggrs = []
        datetimes = []
        values = []
        for attr_name in self.attributes:
            for pixel_timeserie in self.values(attr_name):
                for i in range(0, len(self.timeline)):
                    datetimes.append(self.timeline[i])
                    attrs.append(attr_name)
                    values.append(pixel_timeserie[i])

        df = pd.DataFrame({
            'attribute': attrs,
            'datetime': pd.to_datetime(datetimes, format="%Y-%m-%dT%H:%M:%SZ", errors='ignore'),
            'value': values,
        })
        
        return df


    def plot(self, **options):
        """Plot the time series on a chart.

        Keyword Args:
            attribute (string): An attribute, like 'EVI' or 'EVI'.

        Raises:
            ImportError: If Maptplotlib or Numpy or Datetime could not be imported.

        .. note::
            You should have Matplotlib and Numpy installed.
            See :ref:`wtss.py install notes <Installation>` for more information.
        """
        try:
            import datetime as dt

            import matplotlib.pyplot as plt
            import numpy as np
        except:
            raise ImportError('Could not import some of the packages [datetime, matplotlib, numpy].')

        # Check options (only valid is 'attributes')
        for option in options:
            if option!='attribute':
                raise Exception('Only available options is "attribute"')

        # Get attribute value if user defined, otherwise use the first
        attribute = options['attribute'] if 'attribute' in options else self.attributes[0]
        if not isinstance(attribute, str):
            raise Exception('attributes must be a string', attribute)

        # Create plot
        fig, ax = plt.subplots()

        # Add timeserie for each pixel
        x = [dt.datetime.strptime(d, '%Y-%m-%dT%H:%M:%SZ').date() for d in self.timeline]
        attribute_timeseries = self.values(attribute)
        for pixel_ts in attribute_timeseries:
            ax.plot(x, pixel_ts, ls='-', linewidth=1.5)

        # Define plot properties and show plot
        plt.title(f'{self._coverage.name}', fontsize=20)
        plt.xlabel('Date', fontsize=16)
        plt.ylabel(attribute, fontsize=16)
        plt.grid(b=True, color='gray', linestyle='--', linewidth=0.5)
        fig.autofmt_xdate()
        plt.show()


    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints a time series."""
        return self._repr_html_()


    def _repr_html_(self):
        """Display the time series as a HTML.

        This integrates a rich display in IPython.
        """
        html = render_html('timeseries.html', timeseries=self)

        return html