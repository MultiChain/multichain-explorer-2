MultiChain Explorer 2
=====================

[MultiChain Explorer 2](https://github.com/MultiChain/multichain-explorer-2) is a new blockchain browser for [MultiChain](http://www.multichain.com/) blockchains.

Below are some key differences from the previous [MultiChain Explorer](https://github.com/MultiChain/multichain-explorer):

* Contains no local database or state — all information comes from the node's API.
* Supports multiple blockchains simultaneously.
* No longer reads local MultiChain files, so it can run on a remote server.
* Runs on Python 3 rather than Python 2.
* Requires MultiChain 2.2 beta 3 or later with the `explorersupport` runtime parameter.

Requirements
------------

* Python 3.x
* MultiChain 2.2 beta 3 or later

Installation
------------

To install MultiChain Explorer 2 for the current user:

    git clone https://github.com/MultiChain/multichain-explorer-2.git

For new blockchains
-------------------

If you do not yet have a blockchain to explore, [download and install](http://www.multichain.com/download-install/) MultiChain 2.2 beta 3 or later, then create and initialize a new chain as follows:

    multichain-util create chain1
    multichaind chain1 -daemon -explorersupport=2
    
You may optionally choose a name other than `chain1` and adjust the [blockchain parameters](https://www.multichain.com/developers/blockchain-parameters/) before running `multichaind` above.
    
For existing blockchains
------------------------

To use the Explorer with an existing blockchain, [upgrade one of its nodes](https://www.multichain.com/developers/upgrading-nodes-chains/) to MultiChain 2.2 beta 3 or later, then restart it as follows:

    multichaind chain1 -daemon -rescan -explorersupport=2
    
Substitute `chain1` with the chain's name as appropriate. After the first run, the extra parameters are no longer required:

    multichaind chain1 -daemon
    
Supporting the Explorer adds storage and processing requirements to a node. To remove Explorer support, stop the node then restart it as follows:

    multichaind chain1 -daemon -rescan -explorersupport=0

As before, after this first run, the `rescan` and `explorersupport` parameters are no longer required.
    
Configuring the Explorer
------------------------

The bundled example config file `example.ini` can be used as a template for your own configuration.

Explorer 2 supports multiple nodes and/or chains, whether local or remote. Each section of the `.ini` file describes a single node that the Explorer will retrieve information from, using that node's [JSON-RPC API](https://www.multichain.com/developers/json-rpc-api/). The following values may be set for each node:

* `name` (required) – the name of the blockchain.
* `datadir` (optional, local nodes only) – path of the node's blockchain directory (otherwise default assumed).
* `rpchost` (required for remote nodes) – hostname or IP address of the node, with the `http://` or `https://` prefix.
* `rpcport` (optional for local, required for remote) – port for the node's API.
* `rpcuser` (optional for local, required for remote) – username for the node's API.
* `rpcpassword` (optional for local, required for remote) – password for the node's API.

If omitted for a local node, the `rpcport`, `rpcuser` and `rpcpassword` parameters are read from the `multichain.conf` file in the node's blockchain directory. If `rpcport` is not found there, the `default-rpc-port` value from `params.dat` is used.

Using the Explorer
------------------

To start, stop or check the Explorer's status, run the following command from its directory:

    python3 -m explorer config.ini ( daemon | stop | status )
    
Substitute `config.ini` for the name of the `.ini` file you created. By default, the Explorer is started and kept in the foreground. If one of the optional commands is provided, it acts as follows:

* `daemon` – run the Explorer in the background.
* `stop` – stop the Explorer running in the background.
* `status` – get the Explorer's background status.
