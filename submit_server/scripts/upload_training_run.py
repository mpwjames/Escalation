import hashlib
import tempfile
import os
import git
import yaml
import requests
import pandas as pd
import argparse
import sys

#don't judge me -- cute way to import the utils module from two dirs up
base=os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(base,'../../'))
import utils
                
parser = argparse.ArgumentParser()
parser.add_argument('--endpoint',help="Rest endpoint",default='http://escalation.sd2e.org/admin')
parser.add_argument('--debug',help="Use debug manifest and dev endpoint",action='store_true')
parser.add_argument('--githash',help="FOR DEBUG ONLY")
parser.add_argument('--key',help="admin secret key",default='secret')
args=parser.parse_args()

if args.githash and not args.debug:
    print("Can only pass in custom githash in debug mode")
    exit()
    
if args.debug and args.endpoint == 'http://escalation.sd2e.org/admin':
    args.endpoint = 'http://127.0.0.1:5000/admin'

print("POSTing to",args.endpoint)    


if not args.debug:
    while True:
        a = input("Do you want to upload to the production server? [yes/no]:")
        if a == "yes":
            break
        elif a == "no":
            exit()

versioned_datasets_repo_path = utils.get_versioned_data_repo_directory()
git_sha, git_username = utils.get_git_info(versioned_datasets_repo_path)
files = utils.get_files_of_necessary_types(versioned_datasets_repo_path,args.debug)

def y_or_no():
    while True:
        a = input("Do you want to upload crank %s [yes/no]:" % crank)
        if a == "yes":
            return True
        elif a == "no":
            return False
    
if args.githash:
    git_sha = args.githash
#TODO: check if manifest is clean or dirty!

for crank in files:
    # very hardcoded pths
    if not y_or_no():
        continue
    
    perovskitedata = os.path.join(versioned_datasets_repo_path,'data','perovskite',files[crank]['perovskitedata'])
    perovskite_csv=tempfile.mkstemp()[1]
    print("Filtering",perovskitedata,"to",perovskite_csv)

    #TODO: turn into a file and reduce I/O
    df2 = pd.read_csv(perovskitedata,comment='#',dtype={'dataset': 'str'})
    df2 = df2[['dataset','name','_out_crystalscore','_rxn_M_acid','_rxn_M_inorganic','_rxn_M_organic','_rxn_organic-inchikey']]
    orig_len = len(df2)
    df2 = df2[~df2._out_crystalscore.isna()]
    if len(df2) != orig_len:
        print("WARNING: Removed %d NA values from perovskitesdata before uploading" % (orig_len  - len(df2)))
    df2._out_crystalscore = df2._out_crystalscore.astype(int)
    df2.to_csv(perovskite_csv,index=False)

    print("Pushing %d rows from %s to %s . Could take a minute or two." % (len(df2),perovskite_csv,args.endpoint))

    print("crank:",crank)
    print("githash:", git_sha[:7])
    print("username:",git_username)
    r = requests.post(args.endpoint, headers={'User-Agent':'escalation'},
                      data={'crank':crank,'githash':git_sha[:7], 'username':git_username,'adminkey':args.key,'submit':'training_run'},
                      files={ 'perovskitedata':open(perovskite_csv,'rb')},timeout=300)
    print(r.status_code, r.reason,r)
    try:
        print(r.json())
    except:
        pass