import click
import subprocess

@click.command()
@click.option('--name', prompt='Your codebase name',
              help='The name of your project')
@click.option('--cvs', prompt='Your cvs type', help='git, hg or svn')
@click.option('--after', default='1960-01-01', prompt='Starting date', help='Format: yyyy-mm-dd')
@click.option('--before', default='2050-01-01', prompt='Finish date', help='Format: yyyy-mm-dd')

def csi(name, cvs, after, before):
    click.echo("Let's study your %s proyect saved in %s!" % (name, cvs))
    click.echo("Starting Delorean...fasten your seatbelts")
    click.echo("We will travel from %s" % after)
    click.echo("We will stop at %s" % before)
    click.echo("")
    click.echo("")

    evolution = "git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat --after={0} --before={1} > {2}_evo.log"\
        .format(after, before, name)
    subprocess.call(evolution.split(' '))



if __name__ == '__main__':
    csi()