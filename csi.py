import os
import sys
import click
from subprocess import call
from wordcloud import WordCloud

maat = '~/code-maat/ixmaat0.8.5/maat'
merge_maat = 'python ~/code-maat/scripts\ 4/merge_comp_freqs.py'
hotspots_maat = 'python ~/code-maat/scripts\ 4/csv_as_enclosure_json.py'
main_devs_maat = 'python ~/code-maat/scripts\ 4/csv_main_dev_as_knowledge_json.py'


@click.command()
@click.option('--project_name', prompt='Your codebase name',
              help='The name of your project')
@click.option('--after', default='2005-01-01', prompt='Starting date', help='Format: yyyy-mm-dd')
@click.option('--before', default='2020-01-01', prompt='Finish date', help='Format: yyyy-mm-dd')
@click.option('--excluded_dirs', default='.git,.idea,node_modules,typings,coverage,dist,libs,styleguide,assets,docs,static', prompt='Excluded dirs separatted by commas', help='Example: node_modules,.idea,coverage')

def csi(project_name, after, before, excluded_dirs):

    vcs = detect_vcs()

    click.echo("Let's study your %s project saved in %s!" % (project_name, vcs))
    click.echo("Starting Delorean...fasten your seatbelts")
    click.echo("We will travel from %s" % after)
    click.echo("We will stop at %s" % before)
    click.echo("")
    click.echo("")

    call("mkdir -p csi", shell=True)

    generate_evolution(vcs, after, before, project_name)

    generate_summary(vcs, project_name)

    generate_revisions(vcs, project_name)

    execute_cloc(excluded_dirs, project_name)

    merge_revisions_and_lines(project_name)

    copy_d3_files()

    generate_hotspots_json(project_name)

    analyze_soc(vcs, project_name)

    analyze_temporal_coupling(vcs, project_name)

    extract_commit_messages(vcs, after, before, project_name)

    create_word_cloud(project_name)

    analyze_main_developers(vcs, project_name)

    calculate_individual_contributions(vcs, project_name)

    calculate_entity_effort(vcs, project_name)

    generate_main_devs_json(project_name)

    open_server()

    click.echo("Todo ha salido a pedir de Milhouse")


def detect_vcs():
    click.echo("Looking for vcs...")
    if os.path.isdir('./.git'):
        click.echo("GIT setup detected")
        return 'git'
    elif os.path.isdir('./.hg'):
        click.echo("MERCURIAL setup detected")
        return 'hg'
    else:
        click.echo("We could not detect valid vcs. Are you in the main folder? [use git or hg]")
    sys.exit(1)



def open_server():
    click.echo("Opening server...")
    call("cd csi", shell=True)
    # call("python -m SimpleHTTPServer", shell=True)


def calculate_entity_effort(vcs, project_name):
    entity_effort = maat + " -l ./csi/{0}_evo.log -c {1} -a entity-effort > ./csi/{0}_entity_effort.csv".format(
        project_name, vcs)
    click.echo("Calculating identity effort...")
    call(entity_effort, shell=True)


def calculate_individual_contributions(vcs, project_name):
    entity_ownership = maat + " -l ./csi/{0}_evo.log -c {1} -a entity-ownership > ./csi/{0}_entity_ownership.csv".format(
        project_name, vcs)
    click.echo("Calculating individual contributions...")
    call(entity_ownership, shell=True)


def analyze_main_developers(vcs, project_name):
    main_devs = maat + " -l ./csi/{0}_evo.log -c {1} -a main-dev > ./csi/{0}_main_devs.csv".format(project_name, vcs)
    click.echo("Analyzing main developers...")
    call(main_devs, shell=True)


def create_word_cloud(project_name):
    click.echo("Generating word cloud...")
    text = open("./csi/{0}_commits.log".format(project_name)).read()
    wordcloud = WordCloud(width=2000, height=1000, background_color="white").generate(text)
    image = wordcloud.to_image()
    image.save("./csi/{0}_commitcloud.bmp".format(project_name))
    image.show()


def extract_commit_messages(vcs, after, before, project_name):
    if vcs == 'hg':
        commit_messages = """hg log --template "{{desc}}\n" --date '>{0}' --date '<{1}' > ./csi/{2}_commits.log"""\
            .format(after, before, project_name)
    elif vcs == 'git':
        commit_messages = "git log --pretty=format:'%s' --after={0} --before={1} > ./csi/{2}_commits.log" \
            .format(after, before, project_name)

    click.echo("Extracting all commit messages...")
    call(commit_messages, shell=True)


def analyze_temporal_coupling(vcs, project_name):
    temporal_coupling = maat + " -l ./csi/{1}_evo.log -c {0} -a coupling > ./csi/{1}_coupling.csv".format(vcs, project_name)
    click.echo("Analyzing temporal coupling...")
    call(temporal_coupling, shell=True)


def analyze_soc(vcs, project_name):
    sum_coupling = maat + " -l ./csi/{1}_evo.log -c {0} -a soc > ./csi/{1}_soc.csv".format(vcs, project_name)
    click.echo("Analyzing sum of coupling...")
    call(sum_coupling, shell=True)


def copy_d3_files():
    click.echo("Copying D3 files...")
    copy_d3 = "cp -rf ~/code-maat/scripts\ 4/d3 ./csi/"
    call(copy_d3, shell=True)


def generate_hotspots_json(project_name):
    to_json = hotspots_maat + " --structure ./csi/{0}_cloc.csv --weights ./csi/{0}_freq.csv > ./csi/d3/d3-merge.json"\
        .format(project_name)
    click.echo("Generating Hotspots JSON...")
    call(to_json, shell=True)

def generate_main_devs_json(project_name):
    to_json = main_devs_maat + " --structure ./csi/{0}_cloc.csv --owners ./csi/{0}_main_devs.csv " \
                               "--authors ./csi/d3/author_colors.csv > ./csi/d3/d3-main-devs.json"\
        .format(project_name)
    click.echo("Generating Main devs JSON...")
    call(to_json, shell=True)


def merge_revisions_and_lines(project_name):
    merge = merge_maat + " ./csi/{0}_freq.csv ./csi/{0}_cloc.csv > ./csi/{0}_merge.csv".format(project_name)
    click.echo("Merging revisions and lines...")
    call(merge, shell=True)


def execute_cloc(excluded_dirs, project_name):
    cloc = "cloc ./ --by-file --csv --quiet --exclude-dir {0} > ./csi/{1}_cloc.csv".format(excluded_dirs, project_name)
    click.echo("Executing cloc...")
    click.echo(cloc)
    call(cloc, shell=True)


def generate_revisions(vcs, project_name):
    revisions = maat + " -l ./csi/{0}_evo.log -c {1} -a revisions > ./csi/{0}_freq.csv".format(project_name, vcs)
    click.echo("Generating revisions...")
    call(revisions, shell=True)


def generate_summary(vcs, project_name):
    summary = maat + " -l ./csi/{0}_evo.log -c {1} -a summary > ./csi/{0}_summary.txt".format(project_name, vcs)
    click.echo("Generating summary...")
    call(summary, shell=True)


def generate_evolution(vcs, after, before, project_name):
    if vcs == 'git':
        evolution = "git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat --after={0} --before={1} > ./csi/{2}_evo.log" \
            .format(after, before, project_name)
    else:
        evolution = """hg log --template "rev: {{rev}} author: {{author}} date: {{date|shortdate}} files:\n{{files %'{{file}}\n'}}\n" --date '>{0}' --date '<{1}' > ./csi/{2}_evo.log""" \
            .format(after, before, project_name)

    click.echo("Generating evolution...")
    call(evolution, shell=True)


if __name__ == '__main__':
    csi()