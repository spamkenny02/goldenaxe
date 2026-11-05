"""Suppress only secondary rendering while preserving unassisted replay gates."""
import json
import sys
from pathlib import Path

import natural_combat_beam as beam
import unassisted_dungeon_continuation as continuation
from archive_lossless_evidence import sha
from prediction_video_skip import enable_prediction_video_skip
from run_core import ROOT


def main():
    arguments = list(sys.argv[1:])
    assert '--sms' not in arguments and '--controlled-sram-prefix' not in arguments
    original = beam.BeamSecondary.__init__

    def initialize(secondary, *args, **kwargs):
        original(secondary, *args, **kwargs)
        enable_prediction_video_skip(secondary)

    beam.BeamSecondary.__init__ = initialize
    try:
        continuation.main()
    finally:
        beam.BeamSecondary.__init__ = original
    trial = arguments[arguments.index('--trial') + 1]
    region = 'pal' if '--pal' in arguments else 'auto'
    path = ROOT/f'validation/natural-dungeon-combat/md-{region}-{trial}/report.json'
    report = json.loads(path.read_bytes())
    assert report['unassisted_extension'] and not report['primary_state_imports']
    assert not report['new_assistance_writes']
    assert report['full_ram_prediction_matches'] == report['verified_persistent_prediction_windows']
    assert not report['stack_only_difference_windows']
    report.update(secondary_video_suppressed=True, primary_video_suppressed=False,
                  secondary_audio_enabled=True, fast_savestate_format=False,
                  prediction_video_wrapper_sha256=sha(Path(__file__).read_bytes()),
                  prediction_video_adapter_sha256=sha((ROOT/'tools/prediction_video_skip.py').read_bytes()))
    path.write_bytes((json.dumps(report,indent=2)+'\n').encode())


if __name__ == '__main__':
    main()
