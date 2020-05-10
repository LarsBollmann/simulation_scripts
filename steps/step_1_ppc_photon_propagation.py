#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/icetray-start
#METAPROJECT /mnt/lfs7/user/mhuennefeld/software/icecube/py3-v4.1.0/combo_V01-00-00-RC0/build
from __future__ import division
import os
import click
import yaml

from I3Tray import I3Tray
from icecube import icetray

from utils import create_random_services, get_run_folder


@click.command()
@click.argument('cfg', type=click.Path(exists=True))
@click.argument('run_number', type=int)
@click.option('--scratch/--no-scratch', default=True)
def main(cfg, run_number, scratch):
    with open(cfg, 'r') as stream:
        cfg = yaml.full_load(stream)
    cfg['run_number'] = run_number
    cfg['run_folder'] = get_run_folder(run_number)
    if scratch:
        outfile = cfg['scratchfile_pattern'].format(**cfg)
    else:
        outfile = cfg['outfile_pattern'].format(**cfg)
    outfile = outfile.replace(' ', '0')

    click.echo('Run: {}'.format(run_number))
    click.echo('Outfile: {}'.format(outfile))

    # -----------------------------
    # Set PPC environment variables
    # -----------------------------
    ppc_config = cfg['ppc_config']

    # define default Environment variables
    default_ppc_environment_variables = {
        'PPCTABLESDIR': "$I3_BUILD/ice-models/resources/models/spice_bfr-dv1_complete",
        'OGPU': '1',  # makes sure only GPUs are used (with OpenCL version)
    }
    ppc_environment_variables = dict(default_ppc_environment_variables)
    ppc_environment_variables.update(ppc_config['environment_variables'])

    # define default PPC arguments
    default_ppc_arguments = {
        'gpu': 1,
        'MCTree': 'I3MCTree',
    }
    ppc_arguments = dict(default_ppc_arguments)
    ppc_arguments.update(ppc_config['arguments'])

    click.echo('PPC Settings:')
    for key, value in ppc_environment_variables.items():
        click.echo('\t{}: {}'.format(key, os.path.expandvars(value)))
        os.putenv(key, os.path.expandvars(value))

    click.echo('PPC Arguments:')
    for key, value in ppc_arguments.items():
        click.echo('\t{}: {}'.format(key, value))

    # importing ppc must be done *after* setting the environment variables
    from icecube import ppc
    # ------------------------------

    # get random service
    random_services, _ = create_random_services(
        dataset_number=cfg['dataset_number'],
        run_number=cfg['run_number'],
        seed=cfg['seed'],
        n_services=1,
        use_gslrng=cfg['random_service_use_gslrng'])
    random_service = random_services[0]

    # --------------------------------------
    # Build IceTray
    # --------------------------------------
    tray = I3Tray()

    # run PPC
    tray.context["I3RandomService"] = random_service
    tray.AddModule("i3ppc", **ppc_arguments)

    click.echo('Output: {}'.format(outfile))
    tray.AddModule("I3Writer", "writer",
                   Filename=outfile,
                   Streams=[icetray.I3Frame.DAQ,
                            icetray.I3Frame.Physics,
                            icetray.I3Frame.Stream('S'),
                            icetray.I3Frame.Stream('M')])
    # --------------------------------------

    click.echo('Scratch: {}'.format(scratch))
    tray.AddModule("TrashCan", "the can")
    tray.Execute()
    tray.Finish()


if __name__ == '__main__':
    main()