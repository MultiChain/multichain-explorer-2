MultiChain Explorer
===================

MultiChain Explorer is a free blockchain browser for [MultiChain](http://www.multichain.com/) blockchains.

https://github.com/MultiChain/multichain-explorer

    Copyright(C) Coin Sciences Ltd.


Welcome to MultiChain Explorer!
===============================

MultiChain Explorer is still under development, so things may break or change!


System Requirements
-------------------

You must have Python 3.x installed on your system to run MultiChain Explorer.

MultiChain Compatibility
------------------------

MultiChain Explorer currently requires 2.2 beta 2+.

Installation
------------

To install MultiChain Explorer for the current user (recommended):

    git clone https://github.com/MultiChain/multichain-explorer-2.git

Create and launch a MultiChain blockchain
-----------------------------------------

If you do not yet have a chain you want to explore, [Download MultiChain](http://www.multichain.com/download-install/) to install MultiChain and create a chain named ````chain1```` as follows:

    multichain-util create chain1
    multichaind chain1 -daemon -explorersupport=1



Configure the Explorer
----------------------

The bundled example config file ````example.ini```` can be used as a template for your own chain.

The Explorer can support multiple nodes on the same chain, local and remote, and multiple chains. 

Each node/chain should have its own section in .ini file. The following values may be set for each node:

name - Required. Chain name

rpchost - Required for remote nodes.

rpcport - Required for remote nodes. If omitted for local node, the value is taken from multichain.conf. If not found there - 'default-rpc-port' from params.dat

rpcuser - Required for remote nodes. If omitted for local node, the value is taken from multichain.conf.

rpcpassword - Required for remote nodes. If omitted for local node, the value is taken from multichain.conf.

datadir - Optional, only for local nodes. The value of -datadir parameter of MultiChain node if specified.


Launch the Explorer
-------------------

Usage: python3 -m explorer config-file.ini ( daemon | stop | status )

  config-file               Configuration file, see example.ini for examples.
  action                    Optional, one of the following:
      daemon                Start explorer as daemon
      stop                  Stop running explorer
      status                Get explorer status


Examples:


Get usage information:

python3 explorer.py


Start Explorer:

python3 -m explorer config-file.ini daemon


Stop Explorer:

python3 -m explorer config-file.ini stop


