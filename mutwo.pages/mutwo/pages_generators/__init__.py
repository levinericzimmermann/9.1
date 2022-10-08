import numpy

from mutwo import core_events


class EnvelopeDistributionRandom(object):
    def __init__(
        self, offset: float, envelope: core_events.Envelope, random_seed: int = 10
    ):
        self._offset = offset
        self._envelope = envelope
        self._maxima = self._envelope.duration
        self._random = numpy.random.default_rng(seed=random_seed)

    def __call__(self) -> float:
        number = None
        while number is None:
            candidate = self._random.uniform(0, self._maxima)
            likelihood = self._envelope.value_at(candidate)
            if self._random.random() < likelihood:
                number = candidate
        return number + self._offset
