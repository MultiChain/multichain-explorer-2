# -*- coding: utf-8 -*-

# MultiChain Explorer 2 (c) Coin Sciences Ltd
# All rights reserved under BSD 3-clause license


import configparser
import multichain
import utils
import cfg


def is_missing(section, var):
    if var not in section:
        return True
    if section[var] is None:
        return True
    if len(section[var]) == 0:
        return True
    return False


def is_on(section, var):
    if is_missing(section, var):
        return False
    val=str(section[var]).lower()
    if val == 'on':
        return True
    if val == 'yes':
        return True
    if val == 'true':
        return True
    return False
    

def parse_argv(argv):

    args={}
    
    i = 0
    j = 0
    while i < len(argv):
        arg = argv[i]

        if arg[:2] == '--':
            split = arg[2:].split('=', 1)
            if len(split) == 1:
                args[split[0]] = True
            else:
                args[split[0]] = split[1]
        else:
            if j == 0:
                cfg.ini_file=arg
            elif j == 1:
                cfg.action=arg
            j += 1
            
        i += 1
        
    return args

def read_plain_config_file(file_name):
    
    config = configparser.ConfigParser(strict=False)
    with open(file_name) as stream:
        config.read_string("[top]\n" + stream.read())  
    
    settings={}

    for section_name in config:
        section={}
        for var in config[section_name]:
            section[var]=config[section_name][var]
        settings[section_name]=section
        
    return settings["top"]

def read_config_file(file_name):
    
    settings={}
    config = configparser.ConfigParser()
    try:
        config.read(file_name)
    except Exception as error:
        utils.print_error(error)
        return settings
    
    for section_name in config:
        section={}
        for var in config[section_name]:
            section[var]=config[section_name][var]
        settings[section_name]=section
    return settings


def read_conf(args):

    if len(cfg.ini_file) != 0:
        if cfg.ini_file[-4:] != ".ini":
            utils.print_error("Configuration file should have extension .ini")
            return False
                  
        cfg.ini_file=utils.file_dir_name(cfg.ini_file) + utils.file_file_name(cfg.ini_file)
        cfg.settings=read_config_file(cfg.ini_file)
        if len(cfg.settings) != 0:
            if 'main' not in cfg.settings:
                cfg.settings['main']={}
            cfg.settings['main']['ini_dir']=utils.file_dir_name(cfg.ini_file)
    else:
        cfg.settings={'main':{}}
        cfg.settings['main']['ini_dir']=utils.file_dir_name(__file__)
        
    for var in args:
        split = var.split('-', 1)
        if len(split) == 2:
            if split[0] not in cfg.settings:
                cfg.settings[split[0]] = {}
            cfg.settings[split[0]][split[1]]=args[var]
        
    if 'main' not in cfg.settings:
        utils.print_error("Missing main section")
        return False
        
    if is_missing(cfg.settings['main'],'port'):
        utils.print_error("Missing port in main section")
        return False
        
    if is_missing(cfg.settings['main'],'base'):
        cfg.settings['main']['base']="/"
        
    cfg.explorer_name=utils.file_file_name(cfg.ini_file)[:-4]
        
    cfg.ini_dir=cfg.settings['main']['ini_dir']
    cfg.log_file=cfg.ini_dir + cfg.explorer_name + ".log"
    cfg.pid_file=cfg.ini_dir + cfg.explorer_name + ".pid"
    
    if 'chains' not in cfg.settings:
        utils.print_error("Missing chains section")
        return False

    cfg.chains=[]
    
    for chain in cfg.settings['chains']:
        if is_on(cfg.settings['chains'],chain):
            if chain not in cfg.settings:
                utils.print_error("Missing section for selected chain " + str(chain))
                return False
                
            if is_missing(cfg.settings[chain],'name'):
                utils.print_error("Missing name for chain " + str(chain))
                return False
                
            if not is_missing(cfg.settings[chain],'rpchost'):
                if is_missing(cfg.settings[chain],'rpcport'):
                    utils.print_error("Missing rpcport for remote chain " + str(chain))
                    return False
                if is_missing(cfg.settings[chain],'rpcuser'):
                    utils.print_error("Missing rpcuser for remote chain " + str(chain))
                    return False
                if is_missing(cfg.settings[chain],'rpcpassword'):
                    utils.print_error("Missing rpcpassword for remote chain " + str(chain))
                    return False
                if not is_missing(cfg.settings[chain],'datadir'):
                    utils.print_error("datadir parameter specified for chain "  + str(chain) + " (allowed only for local chains)")
                    return False
            else:
                if not multichain.multichain_init_rpc_parameters(chain):
                    utils.print_error("Couldn't retrieve RPC parameters for local chain " + str(chain))
                    return False
                    
            chain_object=multichain.MCEChain(chain)  
            if not chain_object.initialize():
                utils.print_error("Couldn't initialize chain " + str(chain))
                return False
                
            cfg.chains.append(chain_object)              

    if len(cfg.chains) == 0:
        utils.print_error("Explorer chain(s) not selected")
        return False
               
    return True
    

def check_file_config(config):

    if is_missing(config,'dir'):
        config['dir']=cfg.ini_dir
    config['dir']=utils.full_dir_name(config['dir'])
    
    if not utils.check_directory(config['dir']):
        utils.print_error("Couldn't create directory for output " + config["name"])
        return False
    
    if is_missing(config,'ptr'):
        config['ptr']=config['dir'] + config["name"] + ".ptr"
    if is_missing(config,'out'):
        config['out']=config['dir'] + config["name"] + ".out"

    return True


def check_db_config(config,allow_missing=False):
    
    if is_missing(config,'host'):
        config['host']='127.0.0.1'
    if is_missing(config,'dbname'):
        utils.print_error("Missing DB name")
        return False
    if is_missing(config,'user'):
        if allow_missing:
            config['user']=None
        else:
            utils.print_error("Missing DB user")
            return False
    if is_missing(config,'password'):
        if allow_missing:
            config['password']=None
        else:
            utils.print_error("Missing DB password")
            return False
    if is_missing(config,'pointer'):
        utils.print_error("Missing DB pointer")
        return False
        
    config['sql'] = None
    if not is_missing(config,'sql_output'):
        config['sql']=utils.file_dir_name(config['sql_output']) + utils.file_file_name(config['sql_output'])
        config['dir']=utils.file_dir_name(config['sql'])
        if not utils.check_directory(config['dir']):
            utils.print_error("Couldn't create directory for output " + config["name"])
            return False
            
    return True
