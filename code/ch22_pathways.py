"""Original bounded latency bookkeeping, not a measured reflex or diagnostic model."""
import argparse
import json
import math

DEFAULTS = dict(afferentLength=0.6, afferentVelocity=30, motorLength=0.5,
                motorVelocity=50, ascendingLength=1, ascendingVelocity=20,
                localDelay=4, effectorDelay=5, centralDelay=6)


def latency(parameters=None):
    """Metres, m/s and ms inputs; finite synthetic teaching domain only."""
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, dict) or parameters.keys() - DEFAULTS.keys():
        raise ValueError('Known parameter dictionary required')
    p = DEFAULTS | parameters
    for key, value in p.items():
        upper = 10 if key.endswith('Length') else 200 if key.endswith('Velocity') else 100
        lower = 0.1 if key.endswith('Velocity') else 0
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not lower <= value <= upper):
            raise ValueError(f'{key} outside finite teaching domain')
    branch = 1000 * p['afferentLength'] / p['afferentVelocity']
    local = branch + p['localDelay']
    motor = local + 1000 * p['motorLength'] / p['motorVelocity']
    ascending = branch + 1000 * p['ascendingLength'] / p['ascendingVelocity']
    return dict(branch=branch, local=local, motor=motor,
                effector=motor + p['effectorDelay'], ascending=ascending,
                central=ascending + p['centralDelay'])


def check():
    assert latency() == dict(branch=20, local=24, motor=34, effector=39,
                            ascending=70, central=76)
    assert latency(dict(ascendingLength=0))['effector'] == 39
    assert latency(dict(motorLength=0))['motor'] == 24
    for bad in [-1, 0, float('nan'), float('inf'), True, '30']:
        try:
            latency(dict(afferentVelocity=bad))
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid velocity accepted')
    print('Default arrivals, independent branch changes and six invalid velocities pass.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        check()
    else:
        print(json.dumps(latency(), indent=2, allow_nan=False))
