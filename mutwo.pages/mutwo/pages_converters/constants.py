from mutwo import core_events

# Paths
BUILD_PATH = "./builds"
TEMPLATES_PATH = "./templates"
PAGE_TEMPLATE_PATH = f"{TEMPLATES_PATH}/page.tex.j2"
SCORE_TEMPLATE_PATH = f"{TEMPLATES_PATH}/score.tex.j2"
PAGE_COVER_TEMPLATE_PATH = f"{TEMPLATES_PATH}/page-cover.tex.j2"

# Page creation
MINIMA_DURATION_GENERATOR_ENVELOPE = core_events.Envelope([[0, 0.5], [4, 1], [12, 1], [18, 0.7]])
MINIMA_DURATION_GENERATOR_OFFSET = 1

MAXIMA_DURATION_GENERATOR_ENVELOPE = core_events.Envelope([[0, 1], [30, 1], [60, 0.5]])
MAXIMA_DURATION_GENERATOR_OFFSET = 10

PARTY_COUNT_TUPLE = (3, 4, 5)
