"""Reuse the existing cold fixed-input proof core between campaign checkpoints."""
from contextlib import contextmanager
from cold_replay_stream import ReplayStream


@contextmanager
def streamed_replays(helper, folder):
    original=helper.run
    stream=ReplayStream(folder)
    def run(tool,args):
        if tool!='replay_assisted_prefix.py':
            return original(tool,args)
        assert len(args)==2 and args[0]=='--trace', 'Only canonical fixed-input replay requests are shared'
        result=stream.prove(args[1])
        print('SHARED COLD REPLAY',args[1],result['frames'],flush=True)
        return result
    helper.run=run
    try:
        yield stream
    finally:
        helper.run=original
        stream.close()
