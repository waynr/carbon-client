#!/usr/bin/env python
# encoding: utf-8
from .udp import UDPClient
from .metrics import Counter, Timer, Collector
from . import stat


class SimpleMetricBase(object):
    def __init__(self, metric, client=None):
        if client is None:
            client = stat

        assert isinstance(client, UDPClient)
        self._client = client
        self._metric = metric


class SimpleCounter(SimpleMetricBase):
    TYPE = Counter

    def __enter__(self):
        metric = "%s_ok" % self._metric
        self._client[metric] = self.TYPE
        self._client[metric].inc(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            metric = "%s_fail" % self._metric
            self._client[metric] = self.TYPE
            self._client[metric].inc(1)


class SimpleTimer(SimpleMetricBase):
    TYPE = Timer

    def __enter__(self):
        self._done_metric = "%s_ok" % self._metric
        self._fail_metric = "%s_fail" % self._metric

        self._client[self._done_metric] = self.TYPE
        self._client[self._fail_metric] = self.TYPE

        self._done_watch = self._client[self._done_metric].start()
        self._fail_watch = self._client[self._fail_metric].start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            metric = self._done_metric
            watch = self._done_watch
        else:
            metric = self._fail_metric
            watch = self._fail_watch

        self._client[metric].stop(watch)


class SimpleCollector(SimpleMetricBase):
    TYPE = Collector

    def __enter__(self):
        if self._metric not in self._client:
            self._client[self._metric] = self.TYPE

        return self._client[self._metric]

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
