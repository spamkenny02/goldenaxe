"""Parent-wait race regression tests; no emulator or game proof is produced."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import cold_replay_stream as reader


class CompletedProofRace(unittest.TestCase):
    def exercise(self, *, publish, worker_exited):
        with tempfile.TemporaryDirectory(prefix='replay-wait-unit-',dir=reader.ROOT/'validation') as name:
            folder=Path(name).resolve()
            assert folder.is_relative_to((reader.ROOT/'validation').resolve())
            source=folder/'trace';source.mkdir()
            (source/'capture.json').write_text(json.dumps(dict(frames=1)))
            proof=source.with_name(source.name+'-assisted-fixed-replay-1')
            requests=folder/'requests';requests.mkdir()
            def complete():
                if publish:
                    proof.mkdir(exist_ok=True)
                    (proof/'replay_report.json').write_text(json.dumps(dict(passed=True,frames=1,fixture_only=True)))
            def poll():
                if worker_exited:complete();return 0
                return None
            calls=0
            def clock():
                nonlocal calls
                calls+=1
                if calls==1:return 0
                complete();return 601
            stream=SimpleNamespace(folder=requests,suffix='',number=0,
                                   process=SimpleNamespace(poll=poll))
            with patch.object(reader.time,'monotonic',side_effect=clock):
                return reader.ReplayStream.prove(stream,folder.name+'/trace')

    def test_completion_at_deadline_is_accepted(self):
        self.assertTrue(self.exercise(publish=True,worker_exited=False)['fixture_only'])

    def test_deadline_without_proof_still_fails(self):
        with self.assertRaises(TimeoutError):self.exercise(publish=False,worker_exited=False)

    def test_completion_as_worker_exits_is_accepted(self):
        self.assertEqual(self.exercise(publish=True,worker_exited=True)['frames'],1)

    def test_worker_exit_without_proof_still_fails(self):
        with self.assertRaises(RuntimeError):self.exercise(publish=False,worker_exited=True)


if __name__=='__main__':unittest.main()
