PyCoin - the Python blockchain
==============================

This is a blockchain written purely in Python.

Features:

- wallet creation and management
- easy to setup node (one command)
- create transactions
- live blockchain inspection via node HTTP API (flask)
- Proof of work block generation
- storage via sqlite - simple and lightweight with no extra dependencies as
  sqlite3 is available in python stdlib
- programmatic interaction with the node via HTTP Api and client class

Roadmap:

- [ ] wallet recovery via mnemonic seed
- [ ] externalize miner from node
- [ ] implement mining reward system
- [ ] refactor so that some parts would be easy extended/replaced (communication
  protocol, wallet class, proof of work, blockchain storage)
- [ ] distributed consensus algorithm


Installation
------------

::

    pip install git+https://github.com/vladcalin/pycoin

Create a wallet
---------------

::

    pycoin-wallet create mywallet
    # is generated in ~/.pycoin/wallet/mywallet

List wallets
------------

::

    pycoin-wallet list
    mywallet1
    mywallet2
    mywallet3

Inspect wallet
--------------

In order to show the transactions, you must have a node running locally or
pass another node's address as options
::

    pycoin-wallet inspect vlad [--node=address:port]
    Wallet info
    address = Ft2MXvu4sZUV42zD9AP-FBvB4k5fogDHX5z.py
    balance = 25.0
    transactions:
    + 50.0 (reward)
    - 10.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py
    - 10.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py
    - 1.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py
    - 1.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py
    - 1.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py
    - 1.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py
    - 1.0 to 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py

Send money to another address
-----------------------------

In order to work, you must have a node running locally, or pass a node's address
as an extra option
::

    pycoin-wallet transaction create mywallet 4HYFUbLOpf_HdxSMxH2kyCmHK2g-SGwVjjq.py 10.0 [--node=address:port]
    # mywallet <wallet_name> <receiver address> <amount>


Node API
--------

- ``/blockchain/blocks[?verbose=true&start=:int&end=:int]`` - view all blocks. ``verbose`` = show block complete data,
  ``start`` = show starting with that block, ``end`` = show block until that block
- ``wallets/info/<address>`` - view address info (balance + transactions)


License
-------

MIT but I'd like some attribution if you use this stuff in your project
(it's not required but it would be nice).