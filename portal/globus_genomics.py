from __future__ import print_function
from bioblend.galaxy import GalaxyInstance
import time
import optparse
import requests
import sys, os
from bdbag import bdbag_api
import time
import urllib
import tempfile
import glob
import json
import shutil

## Will submit topmed rna-seq workflow with minid: ark:/57799/b9x70v

## command line should be:  python ./submit_topmed_rna_seq.v2.py -k <api_key> -w "ark:/57799/b9x70v" -m "input_minid"

## output will print out after all analysis is complete the output minid.

# usage = "Usage: submit_topmed_rnaseq_workflow.py -k <API_KEY> --input-minid <INPUT_MINID>"
# parser = optparse.OptionParser(usage=usage)
# parser.add_option("-k", "--key",
#                   action="store", type="string",
#                   dest="api_key", help="User API Key")
# parser.add_option("-m", "--input-minid",
#                   action="store", type="string",
#                   dest="input_minid",
#                   help="Input MINID containing BDBag of paired-ended fastq files")
# parser.add_option("-w", "--workflow-minid",
#                   action="store", type="string",
#                   dest="wf_minid",
#                   help="Workflow MINID containing BDBag of workflow to run")
# (opts, args) = parser.parse_args()
#
# if not opts.api_key:  # if api_key is not given
#     parser.error('API_KEY is not given')
# if not opts.input_minid:  # if minid is not given
#     parser.error('Input MINID is not given')
# if not opts.wf_minid:  # if wf is not give
#     parser.error('Workflow MINID is not given')

URL = "https://nihcommons.globusgenomics.org"
# URL="https://dev.globusgenomics.org"
# API_KEY = opts.api_key
# input_minid = opts.input_minid
# wf_minid = opts.wf_minid
# gi = GalaxyInstance(URL, API_KEY)


def submit_job(input_minid, wf_minid, api_key=None):
    #### BASIC ASSUMPTIONS:
    # 1. User has a globus ID and has account in GG
    # 2. User has created an API
    # 3. User does not have the workflow setup on their account

    #### A. Get workflow GA file from the workflow MINID
    #### B. Push GA file to the instance url
    gi = GalaxyInstance(URL, api_key)

    QUERY_BASE = "http://minid.bd2k.org/minid/landingpage/"
    tmp_path = tempfile.mkdtemp()
    wf_mine = None
    try:
        # A.
        BASE_DOWNLOAD_PATH = "/%s" % (tmp_path)
        query = "%s/%s" % (QUERY_BASE, wf_minid)
        # print("Executing query: %s" % query)
        r = requests.get(query, headers={"Accept": "application/json"})
        location = r.json()["locations"][0]['link']
        filename = location.split("/")[-1]
        path = "%s/%s" % (BASE_DOWNLOAD_PATH, filename)
        # print("Downloading result: %s" % location)

        # Save the bag from the minid location
        response = requests.get(location, stream=True)
        with open(path, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)

        extract_path = ".".join(path.split(".")[0:-1])
        output_path = "%s/%s" % (extract_path, ".".join(filename.split(".")[0:-1]))
        # print("Extracting bag and resolving fetch: %s" % output_path)
        bdbag_api.extract_bag(path, extract_path)
        time.sleep(5)
        # print('resolving fetch')
        bdbag_api.resolve_fetch(output_path, True)
        ga_file = glob.glob("%s/data/*.ga" % (output_path))[0]

        # B.
        ga_dict = None
        with open(ga_file) as handle:
            ga_dict = json.loads(handle.read())
        if ga_dict is not None:
            wf_mine = gi.workflows.import_workflow_dict(ga_dict)

    finally:
        shutil.rmtree(tmp_path)
        # print('finished!')

    # published_workflow_id = "6f1411e6cfea8ef7"
    # workflow_name = "imported: RNA-seq-Gtex-stage1-v2.0-bags_transfer"
    #
    ## check if workflow exists
    # workflows = gi.workflows.get_workflows(name=workflow_name)
    # wf_mine = None
    # if len(workflows) > 0:
    #    wf_mine = workflows[-1]
    # else:
    #    # workflow does not exist, need to import from published
    #    wf_mine = gi.workflows.import_shared_workflow(published_workflow_id)

    # create a history
    history_name = "topmed_history_%s" % time.strftime("%a_%b_%d_%Y_%-I:%M:%S_%p",
                                                       time.localtime(time.time()))
    history = gi.histories.create_history(name=history_name)
    wf_data = {}
    wf_data['workflow_id'] = wf_mine['id']
    wf_data['ds_map'] = {}
    parameters = {}
    parameters['0'] = {'minid': input_minid}
    parameters['5'] = {'historyid': history['id'], 'userapi': api_key, 'url': URL}
    wf_data['parameters'] = parameters

    # print('super close to finishing!')

    res = gi.workflows.invoke_workflow(wf_data['workflow_id'], wf_data['ds_map'],
                                       params=wf_data['parameters'],
                                       history_id=history['id'],
                                       import_inputs_to_history=False)
    return {
        'history_name': history_name,
        'history_id': res['history_id'],
        'res': res
    }
    # return input_minid, wf_mine['name'], wf_mine['id'], history_name, res['history_id']
    # print("SUBMITTED\t%s\t%s\t%s\t%s\t%s" % (
    # input_minid, wf_mine['name'], wf_mine['id'], history_name, res['history_id']))
# loop until status is complete
# done = 0
# minid = None

# while not done:
def check_status(api_key, history_id):
    gi = GalaxyInstance(URL, api_key, history_id)

    state = gi.histories.show_history(history_id, contents=False)['state']
    minid = None
    if state == 'ok':
        for content in gi.histories.show_history(history_id, contents=True):
            if "Minid for history" in content['name'] and content[
                'visible'] is True and content['deleted'] is False:
                id = content['id']
                dataset = gi.datasets.show_dataset(id)
                minid = dataset_content['peek'].split("\t")[-1].split("<")[0]
                print(
                    "Your workflow is complete\nYour output MINID is: %s" % minid)
                return {'minid': minid,
                        'dataset': dataset}
    elif state == 'error':
        raise Exception('Error running workflow')

    # else:
    #     print("Workflow running: %s" % (
    #     time.strftime("%a_%b_%d_%Y_%-I:%M:%S_%p", time.localtime(time.time()))))
    #     time.sleep(60)

