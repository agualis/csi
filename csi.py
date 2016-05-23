import click
from subprocess import call

import sys

maat = '~/code-maat/ixmaat0.8.5/maat'
merge_maat = 'python ~/code-maat/scripts\ 4/merge_comp_freqs.py'


@click.command()
@click.option('--project_name', prompt='Your codebase name',
              help='The name of your project')
@click.option('--cvs', prompt='Your cvs type', help='git, hg or svn')
@click.option('--after', default='1960-01-01', prompt='Starting date', help='Format: yyyy-mm-dd')
@click.option('--before', default='2050-01-01', prompt='Finish date', help='Format: yyyy-mm-dd')

def csi(project_name, cvs, after, before):
    click.echo("Let's study your %s proyect saved in %s!" % (project_name, cvs))
    click.echo("Starting Delorean...fasten your seatbelts")
    click.echo("We will travel from %s" % after)
    click.echo("We will stop at %s" % before)
    click.echo("")
    click.echo("")

    if cvs == 'git':
        git_csi(project_name, after, before)
    else:
        click.echo("%s csv not supported [use git or hg]" % cvs)
        sys.exit(1)

    click.echo("Todo ha salido a pedir de Milhouse")

def hg_csi(name, cvs, after, before):
    evolution = """hg log --template "rev: {rev} author: {author} date: {date|shortdate} files:\n{files %'{file}\n'}\n" > roi_evo.log"""

def git_csi(project_name, after, before):
    evolution = "git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat --after={0} --before={1} > {2}_evo.log" \
        .format(after, before, project_name)

    summary = maat + " -l {0}_evo.log -c git -a summary > {0}_summary.txt".format(project_name)

    revisions = maat + " -l {0}_evo.log -c git -a revisions > {0}_freq.csv".format(project_name)

    click.echo("Generating evolution...")
    call(evolution, shell=True)

    click.echo("Generating summary...")
    call(summary, shell=True)

    click.echo("Generating revisions...")
    call(revisions, shell=True)




if __name__ == '__main__':
    csi()