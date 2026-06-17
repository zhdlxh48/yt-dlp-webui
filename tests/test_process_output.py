from __future__ import annotations

from ytdlp_webui.services.process_output import ProcessOutput, ProcessOutputParser
from ytdlp_webui.services.ytdlp_output import YtdlpOutputClassifier


def test_process_output_parser_decodes_cp949_fallback() -> None:
    parser = ProcessOutputParser()

    outputs = parser.feed("중년게이머 김실장\n".encode("cp949"))

    assert outputs[0].text == "중년게이머 김실장"


def test_process_output_parser_marks_carriage_return_as_replace() -> None:
    parser = ProcessOutputParser()

    outputs = parser.feed(b"[download] 10.0% of 1MiB\r")

    assert outputs[0].replace is True


def test_ytdlp_output_classifier_parses_fragment_progress() -> None:
    classifier = YtdlpOutputClassifier()

    progress = classifier.parse_progress(
        ProcessOutput("1: [download] 14.84MiB at 8.11MiB/s (00:00:01) (frag 18/2884)")
    )

    assert progress is not None
    assert progress.stream_id == "1"
    assert progress.fragment == 18
    assert progress.fragment_total == 2884
    assert progress.speed == "8.11MiB/s"


def test_ytdlp_output_classifier_uses_main_stream_for_unprefixed_progress() -> None:
    classifier = YtdlpOutputClassifier()

    progress = classifier.parse_progress(
        ProcessOutput("[download] 12.3% of 10.00MiB at 1.00MiB/s ETA 00:09", replace=True)
    )

    assert progress is not None
    assert progress.stream_id == "main"
    assert progress.percent == 12.3
