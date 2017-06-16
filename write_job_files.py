import os

import click
import yaml

base_dir = os.path.abspath('.')

step_enum = {-1: None,
              0: '0_after_proposal',
              1: '0_after_clsim',
              2: '2',
              3: '3'}


@click.command()
@click.argument('config_file', click.Path(exists=True))
@click.option('--step',
              '-s',
              default=1,
              help='0 = everything upto proposal\n' + \
                   '1 = clsim\n' + \
                   '2 = everythin up to L2')
def main(config_file, step):
    with open(config_file, 'r') as stream:
        config = yaml.load(stream)
    config.update({'step': step_enum[step],
                   'base_dir': base_dir})
    config['e_min'] = float(config['e_min'])
    config['e_max'] = float(config['e_max'])
    config['muongun_e_break'] = float(config['muongun_e_break'])
    config['n_events_per_run'] = int(config['n_events_per_run'])
    config['output_folder'] = config['output_folder'].format(**config)
    config['previous_step'] = step_enum[step - 1]

if __name__ == '__main__':
    main(test='jaja')