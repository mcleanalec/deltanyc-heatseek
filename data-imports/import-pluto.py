#!/usr/bin/env python

import argparse
import os
import os.path
import sys
import logging


from sqlalchemy import create_engine

from utils import *

mkdir_p(BASE_DIR)

logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout,
    level=logging.INFO)
log = logging.getLogger(__name__)

"""
PLUTO IMPORT
Manually Download PLUTO.zip from below, extract to a directory. Run below pointed at that directory.

http://www1.nyc.gov/assets/planning/download/zip/data-maps/open-data/nyc_pluto_16v2%20.zip
"""

PLUTO_KEY = 'pluto'

PLUTO_dtype_dict = {
    'Borough':       'object',
    'Block':       'int64',
    'Lot':       'int64',
    'CD':       'int64',
    'CT2010':       'float64',
    'CB2010':       'float64',
    'SchoolDist':       'float64',
    'Council':       'float64',
    'ZipCode':       'float64',
    'FireComp':       'object',
    'PolicePrct':       'float64',
    'HealthArea':       'float64',
    'SanitBoro':       'float64',
    'SanitDistrict':       'float64',
    'SanitSub':       'object',
    'Address':       'object',
    'ZoneDist1':       'object',
    'ZoneDist2':       'object',
    'ZoneDist3':       'object',
    'ZoneDist4':       'object',
    'Overlay1':       'object',
    'Overlay2':       'object',
    'SPDist1':       'object',
    'SPDist2':       'object',
    'SPDist3':       'object',
    'LtdHeight':       'object',
    'SplitZone':       'object',
    'BldgClass':       'object',
    'LandUse':       'float64',
    'Easements':       'int64',
    'OwnerType':       'object',
    'OwnerName':       'object',
    'LotArea':       'int64',
    'BldgArea':       'int64',
    'ComArea':       'int64',
    'ResArea':       'int64',
    'OfficeArea':       'int64',
    'RetailArea':       'int64',
    'GarageArea':       'int64',
    'StrgeArea':       'int64',
    'FactryArea':       'int64',
    'OtherArea':       'int64',
    'AreaSource':       'int64',
    'NumBldgs':       'int64',
    'NumFloors':       'float64',
    'UnitsRes':       'int64',
    'UnitsTotal':       'int64',
    'LotFront':       'float64',
    'LotDepth':       'float64',
    'BldgFront':       'float64',
    'BldgDepth':       'float64',
    'Ext':       'object',
    'ProxCode':       'float64',
    'IrrLotCode':       'object',
    'LotType':       'float64',
    'BsmtCode':       'float64',
    'AssessLand':       'int64',
    'AssessTot':       'int64',
    'ExemptLand':       'int64',
    'ExemptTot':       'int64',
    'YearBuilt':       'int64',
    'YearAlter1':       'int64',
    'YearAlter2':       'int64',
    'HistDist':       'object',
    'Landmark':       'object',
    'BuiltFAR':       'float64',
    'ResidFAR':       'float64',
    'CommFAR':       'float64',
    'FacilFAR':       'float64',
    'BoroCode':       'int64',
    'BBL':       'int64',
    'CondoNo':       'int64',
    'Tract2010':       'int64',
    'XCoord':       'float64',
    'YCoord':       'float64',
    'ZoneMap':       'object',
    'ZMCode':       'object',
    'Sanborn':       'object',
    'TaxMap':       'float64',
    'EDesigNum':       'object',
    'APPBBL':       'float64',
    'APPDate':       'object',
    'PLUTOMapID':       'int64'
}



PLUTO_df_keep_cols = [
    'Borough',
    'Block',
    'Lot',
    'CD',
    'CT2010',
    'CB2010',
    'SchoolDist',
    'Council',
    'ZipCode',
    'FireComp',
    'PolicePrct',
    'HealthArea',
    'SanitBoro',
    'SanitDistrict',
    'SanitSub',
    'Address',
    'ZoneDist1',
    'ZoneDist2',
    'ZoneDist3',
    'ZoneDist4',
    'Overlay1',
    'Overlay2',
    'SPDist1',
    'SPDist2',
    'SPDist3',
    'LtdHeight',
    'SplitZone',
    'BldgClass',
    'LandUse',
    'Easements',
    'OwnerType',
    'OwnerName',
    'LotArea',
    'BldgArea',
    'ComArea',
    'ResArea',
    'OfficeArea',
    'RetailArea',
    'GarageArea',
    'StrgeArea',
    'FactryArea',
    'OtherArea',
    'AreaSource',
    'NumBldgs',
    'NumFloors',
    'UnitsRes',
    'UnitsTotal',
    'LotFront',
    'LotDepth',
    'BldgFront',
    'BldgDepth',
    'Ext',
    'ProxCode',
    'IrrLotCode',
    'LotType',
    'BsmtCode',
    'AssessLand',
    'AssessTot',
    'ExemptLand',
    'ExemptTot',
    'YearBuilt',
    'YearAlter1',
    'YearAlter2',
    'HistDist',
    'Landmark',
    'BuiltFAR',
    'ResidFAR',
    'CommFAR',
    'FacilFAR',
    'BoroCode',
    'BBL',
    'CondoNo',
    'Tract2010',
    'XCoord',
    'YCoord',
    'ZoneMap',
    'ZMCode',
    'Sanborn',
    'TaxMap',
    'EDesigNum',
    'APPBBL',
    'APPDate',
    'PLUTOMapID'
]

def main(argv):

    parser = argparse.ArgumentParser(description='Import Pluto dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    pluto_dir = os.path.join(BASE_DIR, PLUTO_KEY)
    mkdir_p(pluto_dir)

    local_pluto_file = os.path.join(pluto_dir, 'pluto.zip')
    pluto_csv = os.path.join(pluto_dir, "pluto.csv")

    if not os.path.isfile(local_pluto_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing Pluto")
        download_file("http://www1.nyc.gov/assets/planning/download/zip/data-maps/open-data/nyc_pluto_16v2%20.zip", local_pluto_file)
    else:
        log.info("Pluto exists, moving on...")

    if not os.path.isfile(pluto_csv) or args.BUST_DISK_CACHE:
        sys.stdout.write("\rUnzipping Pluto archive....")
        unzip(local_pluto_file, pluto_dir)
        sys.stdout.flush()
        sys.stdout.write("\rUnzipping Pluto archive....done.\n")

        sys.stdout.write("\rConcatenating Pluto boro csvs....")
        pluto_csv_files_dir = os.path.join(pluto_dir, "BORO_zip_files_csv")
        pandas_concat_csv(pluto_csv_files_dir, pluto_csv)
        sys.stdout.flush()
        sys.stdout.write("\rConcatenating Pluto boro csvs....done.\n")
    else:
        sys.stdout.write("\rUsing previously concat'ed files....\n")

    PLUTO_date_time_columns = ['appdate']
    PLUTO_description = 'PLUTO'
    PLUTO_input_csv_url = pluto_csv
    PLUTO_pickle = os.path.join(pluto_dir, 'df_PLUTO_NYC.pkl')
    PLUTO_sep_char = ","
    PLUTO_table_name = "pluto_nyc"
    PLUTO_load_pickle = args.LOAD_PICKLE
    PLUTO_save_pickle = args.SAVE_PICKLE
    PLUTO_db_action = "replace"
    PLUTO_truncate_columns = []
    PLUTO_chunk_size = 5000
    PLUTO_max_column_size = 255
    PLUTO_date_format = "%m/%d/%Y"

    hpd_csv2sql(
                PLUTO_description,
                PLUTO_input_csv_url,
                PLUTO_sep_char,
                PLUTO_table_name,
                PLUTO_dtype_dict,
                PLUTO_load_pickle,
                PLUTO_save_pickle,
                PLUTO_pickle,
                PLUTO_db_action,
                PLUTO_truncate_columns,
                PLUTO_date_time_columns,
                PLUTO_chunk_size,
                PLUTO_df_keep_cols,
                PLUTO_max_column_size,
                PLUTO_date_format,
               )

def sql_cleanup(args):
    conn = connect()
    cursor = conn.cursor()

    SQL = '''  
    create index my_idx on my_table(tstamp, user_id, type);
    UPDATE pluto SET address = regexp_replace( address, ' AVE$|-AVE$| -AVE$', ' AVENUE');
    UPDATE pluto SET address = regexp_replace( address, '\.', '', 'g');
    UPDATE pluto SET address = array_to_string(regexp_matches(address, '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE address ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    UPDATE pluto SET address = regexp_replace( address, ' LA$', ' LANE', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' LN$', ' LANE', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' PL$', ' PLACE', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' ST$| STR$', ' STREET', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' RD$', ' ROAD', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' PKWY$', 'PARKWAY', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' PKWY ', ' PARKWAY ', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' BLVD$', ' BOULEVARD', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' BLVD ', ' BOULEVARD ', 'g');
    UPDATE pluto SET address = regexp_replace( address, ' BLVD', ' BOULEVARD ', 'g');
    UPDATE pluto SET address = regexp_replace( address, '^BCH ', 'BEACH ', 'g');
    UPDATE pluto SET address = regexp_replace( address, '^E ', 'EAST ');
    UPDATE pluto SET address = regexp_replace( address, '^W ', 'WEST ');
    UPDATE pluto SET address = regexp_replace( address, '^N ', 'NORTH ');
    UPDATE pluto SET address = regexp_replace( address, '^S ', 'SOUTH '); 

    '''

    for result in cursor.execute(SQL,multi = True):
        pass
    
    conn.commit()
    cursor.close()
    conn.close()

    # Add some indexes


if __name__ == "__main__":
    main(sys.argv[:1])
